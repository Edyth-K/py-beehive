import logging
import socket
import struct
import threading
import time
from dataclasses import dataclass, field
from typing import List, Tuple

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 9_999
    max_players: int = 4
    recv_timeout: float = 1.0          # seconds
    listen_backlog: int = 8
    msg_fmt: str = "ii"                # two signed 32‑bit ints
    log_level: int = logging.INFO


# --------------------------------------------------------------------------- #
# Server
# --------------------------------------------------------------------------- #

class Server:
    """Minimal threaded TCP server that receives pairs of ints from clients."""

    def __init__(self, cfg: ServerConfig = ServerConfig()) -> None:
        self.cfg = cfg
        self._shutdown = threading.Event()
        self._player_lock = threading.Lock()
        self._players: List[socket.socket] = []
        self._threads: List[threading.Thread] = []

        logging.basicConfig(
            level=cfg.log_level,
            format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s",
        )

    # ..................................................................... #
    # Public API
    # ..................................................................... #

    def start(self) -> None:
        """Start listening and (in the main thread) process outgoing work."""
        t = threading.Thread(
            target=self._accept_loop, name="AcceptLoop", daemon=True
        )
        t.start()
        self._threads.append(t)

        logging.info("Server started; press Ctrl‑C to stop.")
        try:
            while not self._shutdown.is_set():
                # ---- place periodic server‑wide work here (e.g. broadcast) ----
                time.sleep(0.05)
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt – shutting down.")
        finally:
            self.stop()

    def stop(self) -> None:
        """Signal all threads to exit and wait for them to finish."""
        if self._shutdown.is_set():
            return                     # already stopping

        logging.info("Stopping server ...")
        self._shutdown.set()

        # close player sockets so their recv() unblocks
        with self._player_lock:
            for p in self._players:
                try:
                    p.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                p.close()

        # wait for every background thread
        for t in self._threads:
            t.join()
        logging.info("Server stopped cleanly.")

    # ..................................................................... #
    # Internals
    # ..................................................................... #

    def _accept_loop(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((self.cfg.host, self.cfg.port))
            srv.listen(self.cfg.listen_backlog)
            srv.settimeout(1.0)        # short timeout to poll shutdown flag

            logging.info(
                "Listening on %s:%d ...", self.cfg.host, self.cfg.port
            )

            while not self._shutdown.is_set():
                try:
                    conn, addr = srv.accept()
                except socket.timeout:
                    continue           # check shutdown flag again
                except OSError:
                    break              # socket closed during shutdown

                if not self._add_player(conn, addr):
                    conn.close()

    def _add_player(self, conn: socket.socket, addr: Tuple[str, int]) -> bool:
        with self._player_lock:
            if len(self._players) >= self.cfg.max_players:
                logging.warning("Rejecting %s – lobby full", addr)
                return False
            self._players.append(conn)

        t = threading.Thread(
            target=self._player_loop,
            args=(conn, addr),
            name=f"Player{addr}",
            daemon=True,
        )
        t.start()
        self._threads.append(t)
        logging.info("Accepted %s. Active players: %d", addr, len(self._players))
        return True

    def _player_loop(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        msg_size = struct.calcsize(self.cfg.msg_fmt)
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        conn.settimeout(self.cfg.recv_timeout)

        try:
            with conn:
                buf = bytearray()
                while not self._shutdown.is_set():
                    try:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break      # orderly shutdown from peer
                        buf.extend(chunk)

                        # process complete messages
                        while len(buf) >= msg_size:
                            part = bytes(buf[:msg_size])
                            del buf[:msg_size]
                            x, y = struct.unpack(self.cfg.msg_fmt, part)
                            logging.debug("Received %s from %s", (x, y), addr)
                    except socket.timeout:
                        continue       # just loop again
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            logging.warning("Lost connection to %s", addr)
        finally:
            with self._player_lock:
                try:
                    self._players.remove(conn)
                except ValueError:
                    pass
            logging.info("Player %s disconnected. Active: %d",
                         addr, len(self._players))

    # ..................................................................... #
    # Optional helper: broadcast binary data to everyone
    # ..................................................................... #

    def broadcast(self, payload: bytes) -> None:
        with self._player_lock:
            dead: List[socket.socket] = []
            for p in self._players:
                try:
                    p.sendall(payload)
                except OSError:
                    dead.append(p)
            for p in dead:             # clean up broken sockets
                self._players.remove(p)
        if dead:
            logging.info("Cleaned up %d dead sockets during broadcast", len(dead))


# --------------------------------------------------------------------------- #
# Launch
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    cfg = ServerConfig(port=9_999, log_level=logging.DEBUG)   # tweak as needed
    Server(cfg).start()
