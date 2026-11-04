package pg.com.hauskaus.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "customers")
data class Customer(
    @PrimaryKey val id: String,
    val name: String,
    val phone: String = "",
    val notes: String = "",
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "ledger_events")
data class LedgerEvent(
    @PrimaryKey val id: String,
    val type: String,
    val amountToea: Long,
    val customerId: String? = null,
    val note: String = "",
    val createdAt: Long = System.currentTimeMillis(),
    val reversesEventId: String? = null,
    val reversalReason: String = ""
)

@Entity(tableName = "repayment_allocations", primaryKeys = ["repaymentEventId", "debtEventId"])
data class RepaymentAllocation(
    val repaymentEventId: String,
    val debtEventId: String,
    val amountToea: Long,
    val reversed: Boolean = false
)
