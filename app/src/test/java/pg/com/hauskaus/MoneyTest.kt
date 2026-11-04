package pg.com.hauskaus

import org.junit.Assert.assertEquals
import org.junit.Test
import java.math.BigDecimal

class MoneyTest {
    @Test fun kinaConvertsExactlyToToea() {
        assertEquals(1235L, BigDecimal("12.35").movePointRight(2).longValueExact())
    }
    @Test(expected = ArithmeticException::class)
    fun rejectsFractionOfToea() {
        BigDecimal("1.001").movePointRight(2).longValueExact()
    }
}
