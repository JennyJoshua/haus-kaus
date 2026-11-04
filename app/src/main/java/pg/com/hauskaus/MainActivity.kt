package pg.com.hauskaus

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.lifecycleScope
import pg.com.hauskaus.data.*
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val repo = LedgerRepository(HausKausDatabase.get(this))
        setContent { MaterialTheme { HausKausScreen(repo) } }
    }
}

@Composable
private fun HausKausScreen(repo: LedgerRepository) {
    var tab by remember { mutableStateOf("Home") }
    var customers by remember { mutableStateOf(emptyList<Customer>()) }
    var events by remember { mutableStateOf(emptyList<LedgerEvent>()) }
    var summary by remember { mutableStateOf(Summary(0,0,0,0,0)) }
    var message by remember { mutableStateOf("") }
    var refresh by remember { mutableIntStateOf(0) }
    LaunchedEffect(refresh) {
        customers = repo.customers()
        events = repo.events()
        summary = repo.summary()
    }
    Scaffold(topBar = { TopAppBar(title = { Text("HausKaus") }) }) { padding ->
        Column(Modifier.padding(padding).fillMaxSize()) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                listOf("Home", "Record", "Customers", "History").forEach { item ->
                    TextButton(onClick = { tab = item }) { Text(item) }
                }
            }
            when (tab) {
                "Home" -> Column(Modifier.padding(16.dp).verticalScroll(rememberScrollState())) {
                    Text("Your business at a glance", style = MaterialTheme.typography.titleLarge)
                    Metric("Cash sales", summary.cashSales)
                    Metric("Expenses", summary.expenses)
                    Metric("Credit sales", summary.creditSales)
                    Metric("Repayments received", summary.repayments)
                    Metric("Customer balances owing", summary.receivables)
                    Text("These figures are records, not a profit calculation.", style = MaterialTheme.typography.bodySmall)
                }
                "Record" -> RecordForm(customers) { type, amount, customer, note ->
                    try { repo.record(type, amount, customer, note); message = "Saved."; refresh++ }
                    catch (e: Exception) { message = e.message ?: "Could not save." }
                }
                "Customers" -> CustomerForm(customers, onAdd = { name, phone ->
                    try { repo.addCustomer(name, phone); message = "Customer saved."; refresh++ }
                    catch (e: Exception) { message = e.message ?: "Could not save." }
                }, onRefresh = { refresh++ })
                else -> LazyColumn(Modifier.padding(12.dp)) {
                    items(events) { event ->
                        ListItem(headlineContent = { Text(event.type.replace('_',' ')) }, supportingContent = { Text(event.note.ifBlank { event.customerId ?: "Business record" }) }, trailingContent = { Text(money(event.amountToea)) })
                    }
                }
            }
            if (message.isNotBlank()) Text(message, Modifier.padding(12.dp), color = MaterialTheme.colorScheme.primary)
        }
    }
}

@Composable private fun Metric(label: String, value: Long) {
    ListItem(headlineContent = { Text(label) }, trailingContent = { Text(money(value), style = MaterialTheme.typography.titleMedium) })
}
private fun money(toea: Long) = "K%,.2f".format(toea / 100.0)

@Composable private fun RecordForm(customers: List<Customer>, onSave: (String, Long, String?, String) -> Unit) {
    var type by remember { mutableStateOf("CASH_SALE") }
    var amount by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }
    var customer by remember { mutableStateOf("") }
    Column(Modifier.padding(16.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text("Record a transaction", style = MaterialTheme.typography.titleLarge)
        var expanded by remember { mutableStateOf(false) }
        Box {
            OutlinedButton(onClick = { expanded = true }) { Text(type.replace('_',' ')) }
            DropdownMenu(expanded, onDismissRequest = { expanded = false }) {
                listOf("CASH_SALE", "CREDIT_SALE", "EXPENSE", "REPAYMENT").forEach { choice ->
                    DropdownMenuItem(text = { Text(choice.replace('_',' ')) }, onClick = { type = choice; expanded = false })
                }
            }
        }
        OutlinedTextField(amount, { amount = it }, label = { Text("Amount in kina (e.g. 12.50)") })
        if (type == "CREDIT_SALE" || type == "REPAYMENT") {
            var customerExpanded by remember { mutableStateOf(false) }
            Box {
                OutlinedButton(onClick = { customerExpanded = true }) { Text(customers.firstOrNull { it.id == customer }?.name ?: "Choose customer") }
                DropdownMenu(customerExpanded, { customerExpanded = false }) {
                    customers.forEach { c -> DropdownMenuItem(text = { Text(c.name) }, onClick = { customer = c.id; customerExpanded = false }) }
                }
            }
        }
        OutlinedTextField(note, { note = it }, label = { Text("Note (optional)") })
        Button(onClick = {
            val parsed = amount.toBigDecimalOrNull()
            if (parsed == null || parsed <= java.math.BigDecimal.ZERO) return@Button
            val toea = try { parsed.movePointRight(2).longValueExact() } catch (_: Exception) { return@Button }
            onSave(type, toea, customer.ifBlank { null }, note)
            amount = ""; note = ""
        }) { Text("Save transaction") }
        Text("Money is stored as whole toea. No internet connection is needed.", style = MaterialTheme.typography.bodySmall)
    }
}

@Composable private fun CustomerForm(customers: List<Customer>, onAdd: (String,String)->Unit, onRefresh: ()->Unit) {
    var name by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    Column(Modifier.padding(16.dp)) {
        Text("Customers", style = MaterialTheme.typography.titleLarge)
        OutlinedTextField(name, { name = it }, label = { Text("Name or nickname") })
        OutlinedTextField(phone, { phone = it }, label = { Text("Phone (optional)") })
        Button(onClick = { onAdd(name, phone); name = ""; phone = "" }) { Text("Add customer") }
        Spacer(Modifier.height(12.dp))
        customers.forEach { ListItem(headlineContent = { Text(it.name) }, supportingContent = { Text(it.phone) }) }
    }
}
