package pg.com.hauskaus.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update

@Dao
interface HausKausDao {
    @Query("SELECT * FROM customers ORDER BY name COLLATE NOCASE") suspend fun customers(): List<Customer>
    @Insert(onConflict = OnConflictStrategy.ABORT) suspend fun addCustomer(customer: Customer)
    @Query("SELECT * FROM ledger_events ORDER BY createdAt DESC") suspend fun events(): List<LedgerEvent>
    @Insert(onConflict = OnConflictStrategy.ABORT) suspend fun addEvent(event: LedgerEvent)
    @Insert(onConflict = OnConflictStrategy.ABORT) suspend fun addAllocation(allocation: RepaymentAllocation)
    @Query("SELECT * FROM ledger_events WHERE type='CREDIT_SALE' AND customerId=:customerId AND reversesEventId IS NULL ORDER BY createdAt, id") suspend fun debts(customerId: String): List<LedgerEvent>
    @Query("SELECT COALESCE(SUM(amountToea),0) FROM repayment_allocations WHERE debtEventId=:debtId AND reversed=0") suspend fun paidOnDebt(debtId: String): Long
    @Query("SELECT * FROM repayment_allocations WHERE repaymentEventId=:repaymentId AND reversed=0") suspend fun allocationsForRepayment(repaymentId: String): List<RepaymentAllocation>
    @Query("UPDATE repayment_allocations SET reversed=1 WHERE repaymentEventId=:repaymentId") suspend fun reverseAllocations(repaymentId: String)
    @Query("SELECT * FROM ledger_events WHERE id=:id LIMIT 1") suspend fun event(id: String): LedgerEvent?
    @Query("SELECT COUNT(*) FROM ledger_events WHERE reversesEventId=:id") suspend fun reversalCount(id: String): Int
    @Query("SELECT COALESCE(SUM(amountToea),0) FROM ledger_events WHERE type='CASH_SALE' AND reversesEventId IS NULL") suspend fun cashSales(): Long
    @Query("SELECT COALESCE(SUM(amountToea),0) FROM ledger_events WHERE type='EXPENSE' AND reversesEventId IS NULL") suspend fun expenses(): Long
    @Query("SELECT COALESCE(SUM(amountToea),0) FROM ledger_events WHERE type='CREDIT_SALE' AND reversesEventId IS NULL") suspend fun creditSales(): Long
    @Query("SELECT COALESCE(SUM(amountToea),0) FROM ledger_events WHERE type='REPAYMENT' AND reversesEventId IS NULL") suspend fun repayments(): Long
}
