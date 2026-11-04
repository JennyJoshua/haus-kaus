package pg.com.hauskaus.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(entities = [Customer::class, LedgerEvent::class, RepaymentAllocation::class], version = 1, exportSchema = false)
abstract class HausKausDatabase : RoomDatabase() {
    abstract fun dao(): HausKausDao
    companion object {
        @Volatile private var INSTANCE: HausKausDatabase? = null
        fun get(context: Context): HausKausDatabase = INSTANCE ?: synchronized(this) {
            INSTANCE ?: Room.databaseBuilder(context.applicationContext, HausKausDatabase::class.java, "hauskaus.db").build().also { INSTANCE = it }
        }
    }
}
