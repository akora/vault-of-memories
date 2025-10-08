"""
Contract: TransactionManager

The TransactionManager coordinates atomic operations between filesystem and database.
"""

from typing import Callable, Any
from dataclasses import dataclass


# Input/Output Types
@dataclass
class TransactionResult:
    """Result of a transaction"""
    success: bool
    result: Any | None
    error: Exception | None
    rollback_performed: bool


# Contract Interface
class TransactionManager:
    """
    Coordinates atomic operations across filesystem and database.
    """

    def execute_transaction(
        self,
        file_operation: Callable[[], Any],
        db_operation: Callable[[], None],
        rollback_file_operation: Callable[[], None] | None = None
    ) -> TransactionResult:
        """
        Execute coordinated file and database operations atomically.

        Contract:
        - MUST begin database transaction before operations
        - MUST execute file operation first
        - MUST execute database operation if file operation succeeds
        - MUST commit database if both operations succeed
        - MUST rollback database if database operation fails
        - MUST rollback file operation if provided and database fails
        - MUST log all operations and outcomes
        - MUST ensure consistent state (both succeed or both fail)

        Args:
            file_operation: Callable that performs file operation
            db_operation: Callable that performs database operation
            rollback_file_operation: Optional callable to rollback file operation

        Returns:
            TransactionResult with operation outcome

        Example:
            ```python
            result = tx_manager.execute_transaction(
                file_operation=lambda: shutil.move(src, dst),
                db_operation=lambda: db.update_file_location(file_id, dst),
                rollback_file_operation=lambda: shutil.move(dst, src)
            )
            ```
        """
        raise NotImplementedError

    def begin(self) -> None:
        """
        Begin a new database transaction.

        Contract:
        - MUST start database transaction
        - MUST initialize rollback tracking
        - MUST be called before execute_transaction
        """
        raise NotImplementedError

    def commit(self) -> None:
        """
        Commit the current database transaction.

        Contract:
        - MUST commit database changes
        - MUST clear rollback tracking
        - MUST handle commit failures
        """
        raise NotImplementedError

    def rollback(self) -> None:
        """
        Rollback the current database transaction.

        Contract:
        - MUST rollback database changes
        - MUST log rollback operation
        - MUST handle rollback failures gracefully
        """
        raise NotImplementedError
