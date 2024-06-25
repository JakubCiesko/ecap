async function getDataFromUrl(url){
    try {
        let response = await fetch(url, 
            {method: "GET",
            headers: {
                "Content-Type": "application/json",
            }}
        );
        if (!response.ok) {
            throw new Error("HTTP error! Status: ${response.status}");
        }
        let data = await response.json();
        return data;
    } catch (error){
        console.error("Error fetching data: ", error);
        return null; 
    }
}

async function getUserExpenses(){
    return getDataFromUrl("/get_user_expenses")
}

async function getUserIncomes(){
    return getDataFromUrl("/get_user_incomes")
}

async function getUserTotalIncome(){return getDataFromUrl("/get_user_total_income");}
async function getUserTotalExpense(){return getDataFromUrl("/get_user_total_expense");}
async function getUserTotalBalance(){return getDataFromUrl("/get_user_total_balance");}
async function getUserSavingGoal(){return getDataFromUrl("/get_user_savings");}

async function updateValues (){
    try {
        const [income, expense, balance, savings] = await Promise.all([
            getUserTotalIncome(), getUserTotalExpense(), getUserTotalBalance(), getUserSavingGoal()
        ]);
        document.getElementById("income").textContent = income.user_income;
        document.getElementById("expense").textContent = expense.user_expense;
        document.getElementById("balance").textContent = balance.user_balance;
        if (savings.user_savings.current.length){
            document.getElementById("savings").textContent = savings.user_savings.current[0] + "/" + savings.user_savings.goal[0];
        }
    } catch (error) {
        console.error("Error updating values: ", error);
    }
}
updateValues();



function createChartConfig(dates, amounts, label){
    const pointColors = Array(amounts.length).fill("rgba(75, 192, 192, 1)");
    const borderColors = Array(amounts.length).fill("rgba(75, 192, 192, 1)");
    return {
        type: "line",
        data: {
            labels: dates,
            datasets: [{
                label: label,
                data: amounts,
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: borderColors,
                borderWidth: 1,
                pointBackgroundColor: pointColors
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        tooltipFormat: "yyyy-mm-dd"
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    }
                    
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount (€)'
                    }
                }
            },
            tooltips: {
                mode: 'index',
                intersect: false
             },
             hover: {
                mode: 'index',
                intersect: false
             }
        }
    };
}


async function get_expected_expenses(){return getDataFromUrl("/get_user_expected_expenses");}
async function get_expected_income(){return getDataFromUrl("/get_user_expected_incomes");}

async function addExpectedDataToChart(dataFetchFunction, chart, label){
    try {
        dataFetchFunction().then(
            data => {if (data) {
                    data = data[Object.keys(data)[0]]; 
                    let dates = data.dates; 
                    let amounts = data.amount; 
                    let color = "#BB436C";
                    for (let index = 0; index <= amounts.length; index++) {
                        let last_label_index = Object.keys(chart.data.labels).length;
                        chart.data.labels[last_label_index] = dates[index];
                        chart.data.datasets[0].data.push(amounts[index]);
                        chart.data.datasets[0].pointBackgroundColor.push(color);
                        chart.data.datasets[0].borderColor.push(color);
                    }
                    chart.data.datasets.push({
                        label: label,
                        backgroundColor: "#BB436C",
                    })
                    chart.update();
                    return true;
                }
                
            }
        )
    } catch (error) {
        console.error("Error adding data to chart: ", error);
    }
}

let userExpensesChart, userIncomesChart;
getUserExpenses().then(data => {
    if (data) {
        data = data.user_expenses;
        const dates = data.date;
        const amounts = Object.values(data.amount);
        let ctx1 = $("#expensesChart").get(0).getContext("2d");
        userExpensesChart = new Chart(ctx1, createChartConfig(dates, amounts, "Expense"));
    }
});
getUserIncomes().then(data => {
    if (data) {
        data = data.user_incomes;
        const dates = data.date;
        const amounts = Object.values(data.amount);
        let ctx2 = $("#incomesChart").get(0).getContext("2d");
        userIncomesChart = new Chart(ctx2, createChartConfig(dates, amounts, "Income"));
    }
});

async function fetchUserExpensesAndCreateChart() {
    try {
        const expensesData = await getUserExpenses();
        if (expensesData && expensesData.user_expenses) {
            const dates = expensesData.user_expenses.date;
            const amounts = Object.values(expensesData.user_expenses.amount);
            const ctx1 = $("#expensesChart").get(0).getContext("2d");
            if (userExpensesChart) {
                userExpensesChart.destroy();
            }

            userExpensesChart = new Chart(ctx1, createChartConfig(dates, amounts, "Expense"));
        }
    } catch (error) {
        console.error('Error fetching user expenses:', error);
    }
}

async function fetchUserIncomesAndCreateChart() {
    try {
        const incomesData = await getUserIncomes();
        if (incomesData && incomesData.user_incomes) {
            const dates = incomesData.user_incomes.date;
            const amounts = Object.values(incomesData.user_incomes.amount);
            const ctx2 = $("#incomesChart").get(0).getContext("2d");
            if (userIncomesChart) {
                userIncomesChart.destroy();
            }

            userIncomesChart = new Chart(ctx2, createChartConfig(dates, amounts, "Income"));
        }
    } catch (error) {
        console.error('Error fetching user incomes:', error);
    }
}

async function addExpectedDataToCharts() {
    try {
        await fetchUserExpensesAndCreateChart();
        await fetchUserIncomesAndCreateChart();

        // After charts are created, add expected data after a slight delay
        setTimeout(async function() {
            await addExpectedDataToChart(get_expected_expenses, userExpensesChart, "Expected Expenses");
            await addExpectedDataToChart(get_expected_income, userIncomesChart, "Expected Income");
        }, 250);

    } catch (error) {
        console.error('Error processing data:', error);
    }
}

addExpectedDataToCharts();

async function generateReport() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (startDate && endDate) {
        try {
            await createUserReport(startDate, endDate); 
            displayUserReports(); 
            $('#reportModal').modal('hide');
        } catch (error) {
            console.error('Error generating report:', error);
            alert('An error occurred while generating the report.');
        }
    } else {
        alert('Please select both start and end dates.');
    }
}


function formatDate(dateStr) {
    const date = new Date(dateStr);
    return `${date.getDate()} ${getMonthName(date.getMonth())} ${date.getFullYear()}`;
}

function getMonthName(month) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months[month];
}

function displayUserReports(){
    getDataFromUrl("get_user_report/").then(
        reports => {
            if (reports) {
                const reportTable = document.getElementById('reportTable');
                if (reportTable.hasChildNodes())
                    reportTable.childNodes.forEach(child=>reportTable.removeChild(child));
                reports.reverse().forEach(report => {
                    const startDateFormatted = formatDate(report.start_date);
                    const endDateFormatted = formatDate(report.end_date);
                    const row = document.createElement('tr');
                    const checkboxCell = document.createElement('td');
                    checkboxCell.innerHTML = '<input class="form-check-input" type="checkbox">';
                    row.appendChild(checkboxCell);
                    const reportID = document.createElement('td');
                    reportID.textContent = report.id;
                    row.appendChild(reportID);
                    const startDateCell = document.createElement('td');
                    startDateCell.textContent = startDateFormatted;
                    row.appendChild(startDateCell);
                    const endDateCell = document.createElement('td');
                    endDateCell.textContent = endDateFormatted;
                    row.appendChild(endDateCell);
                    const incomeCell = document.createElement('td');
                    incomeCell.textContent = report.total_incomes;
                    row.appendChild(incomeCell);
                    const expenseCell = document.createElement('td');
                    expenseCell.textContent = report.total_expenses;
                    row.appendChild(expenseCell);
                    const balanceCell = document.createElement('td');
                    balanceCell.textContent = report.total_incomes - report.total_expenses
                    row.appendChild(balanceCell);
                    const printCell = document.createElement('td');
                    printCell.classList.add('text-center');
                    printCell.innerHTML = "<a class=\"btn btn-sm btn-primary\" href=\"print_report/" + report.id + " \" target=\"_blank\">Print</a>";
                    row.appendChild(printCell);
                    reportTable.appendChild(row);
                })
            }
        } 
    )
}
displayUserReports();
function createUserReport(startDate, endDate){return getDataFromUrl("create_user_report/" + startDate + "/" + endDate);}