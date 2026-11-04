package pg.com.hauskaus.data

import androidx.room.withTransaction
import java.util.UUID

class LedgerRepository(private val db: HausKausDatabase) {
    private val dao = db.dao()
    suspend fun customers() = dao.customers()
    suspend fun events() = dao.events()
    suspend fun addCustomer(name: String, phone: String) {
        require(name.isNotBlank()) { "Enter a customer name." }
        dao.addCustomer(Customer(UUID.randomUUID().toString(), name.trim(), phone.trim()))
    }
    suspend fun record(type: String, amountToea: Long, customerId: String? = null, note: String = "") {
        require(amountToea > 0) { "Amount must be greater than zero." }
        require(type in setOf("CASH_SALE", "CREDIT_SALE", "EXPENSE", "REPAYMENT"))
        if (type == "CREDIT_SALE" || type == "REPAYMENT") require(customerId != null) { "Choose a customer." }
        db.withTransaction {
            val event = LedgerEvent(UUID.randomUUID().toString(), type, amountToea, customerId, note.trim())
            if (type == "REPAYMENT") {
                val debts = dao.debts(customerId!!)
                var remaining = amountToea
                val allocations = debts.mapNotNull { debt ->
                    val outstanding = (debt.amountToea - dao.paidOnDebt(debt.id)).coerceAtLeast(0)
                    val part = minOf(outstanding, remaining)
                    if (part > 0) { remaining -= part; RepaymentAllocation(event.id, debt.id, part) } else null
                }
                require(remaining == 0L) { "Repayment exceeds the customer's outstanding balance." }
                dao.addEvent(event)
                allocations.forEach { dao.addAllocation(it) }
            } else dao.addEvent(event)
        }
    }
    suspend fun reverse(eventId: String, reason: String) {
        require(reason.isNotBlank()) { "Enter a reason for the correction." }
        db.withTransaction {
            val original = dao.event(eventId) ?: error("Transaction not found.")
            require(original.reversesEventId == null) { "A reversal cannot itself be reversed." }
            require(dao.reversalCount(eventId) == 0) { "This transaction has already been reversed." }
            if (original.type == "REPAYMENT") dao.reverseAllocations(original.id)
            if (original.type == "CREDIT_SALE") {
                val paid = dao.paidOnDebt(original.id)
                require(paid == 0L) { "Reverse the repayments allocated to this credit sale first." }
            }
            dao.addEvent(LedgerEvent(UUID.randomUUID().toString(), "REVERSAL", original.amountToea, original.customerId, "Reversal of ${original.id}", reversesEventId = original.id, reversalReason = reason.trim()))
        }
    }
    suspend fun summary(): Summary {
        val cashSales = dao.cashSales()
        val expenses = dao.expenses()
        val credit = dao.creditSales()
        val repaid = dao.repayments()
        val customers = dao.customers()
        var outstanding = 0L
        customers.forEach { customer ->
            dao.debts(customer.id).forEach { debt ->
                outstanding += (debt.amountToea - dao.paidOnDebt(debt.id)).coerceAtLeast(0)
            }
        }
        return Summary(cashSales, expenses, credit, repaid, outstanding)
    }
}
data class Summary(val cashSales: Long, val expenses: Long, val creditSales: Long, val repayments: Long, val receivables: Long)
