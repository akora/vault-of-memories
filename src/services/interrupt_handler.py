"""
Interrupt handler service.

Handles graceful interruption signals (SIGINT, SIGTERM).
"""

import signal
import sys
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline_orchestrator import PipelineOrchestrator

logger = logging.getLogger(__name__)


class InterruptHandler:
    """
    Handles graceful interruption signals (SIGINT, SIGTERM).

    Coordinates with pipeline orchestrator for cleanup and ensures
    data integrity during interruption.
    """

    def __init__(self):
        """Initialize interrupt handler."""
        self._interrupted = False
        self._orchestrator = None

    def register(self, orchestrator: 'PipelineOrchestrator') -> None:
        """
        Register signal handlers for graceful interruption.

        Args:
            orchestrator: Pipeline orchestrator to coordinate with
        """
        self._orchestrator = orchestrator

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.debug("Interrupt handlers registered")

    def _signal_handler(self, signum, frame):
        """
        Handle interrupt signal.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        if self._interrupted:
            logger.warning("Force quit detected - exiting immediately")
            sys.exit(130)

        self._interrupted = True
        logger.info("\nInterrupt received - finishing current operation...")
        logger.info("Press Ctrl+C again to force quit")

        if self._orchestrator:
            self._orchestrator.handle_interruption()

    def is_interrupted(self) -> bool:
        """
        Check if interruption signal was received.

        Returns:
            True if interrupted, False otherwise
        """
        return self._interrupted
