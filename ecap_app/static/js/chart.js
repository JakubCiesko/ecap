

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


const ctx1 = $("#expensesChart").get(0).getContext("2d");
const ctx2 = $("#incomesChart").get(0).getContext("2d");
let userExpensesChart = new Chart(ctx1, {});
let userIncomesChart = new Chart(ctx2, {});


function createChartConfig(dates1, amounts1, dates2, amounts2, label) {
    return {
        type: "line",
        data: {
            labels: dates1.concat(dates2),
            datasets: [
                {
                    label: label,
                    data: dates1.map((date, index) => ({ x: date, y: amounts1[index] })),
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    borderColor: "rgba(75, 192, 192, 1)",
                    borderWidth: 1,
                    pointBackgroundColor: "rgba(75, 192, 192, 1)",
                    fill: false 
                },
                {
                    label: "Expected " + label,
                    data: dates2.map((date, index) => ({ x: date, y: amounts2[index] })),
                    backgroundColor: "#BB436C",
                    borderColor: "#BB436C",
                    borderWidth: 1,
                    pointBackgroundColor: "#BB436C",
                    fill: false 
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        tooltipFormat: "DD-MM-YYYY"
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

async function populateChart(fn1, fn2, chart, ctx){
    try {
        const data1 = await fn1();
        const data2 = await fn2();
        if (data1 && data2) {
            const dates1 = data1.date;
            const amounts1 = data1.amount;
            const dates2 = data2.date;
            const amounts2 = data2.amount;
            if (dates1.length !== amounts1.length || dates2.length !== amounts2.length) {
                console.error('Mismatch between dates and amounts length');
                return;
            }
            let config = createChartConfig(dates1, amounts1, dates2, amounts2, "Expense");
            chart = new Chart(ctx, config);
        } else {
            console.error('Invalid data fetched');
        }
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

async function populateExpenseChart() {
    userExpensesChart.destroy();
    await populateChart(getUserExpenses, getExpectedExpenses, userExpensesChart, ctx1);
}
async function populateIncomeChart() {
    userIncomesChart.destroy();
    await populateChart(getUserIncomes, getExpectedIncome, userIncomesChart, ctx2);
}
let userExpenseDoughnut, userIncomeDoughnut, savingGoalChart
function doughnutConfig(data){
    return {type: "doughnut", data: data}
}

function destroyChart(chartVariable){
    if (chartVariable){
        chartVariable.destroy();
    }
}

async function displayUserExpenseDoughnut(){
    let ctx = $("#expenseCategoriesChart").get(0).getContext("2d");
    let fetchedData = await getDataFromUrl("expense_category/");
    fetchedData = fetchedData.data;
    userExpenseDoughnut = doughNutChart(fetchedData, ctx, userExpenseDoughnut, "Expense Categories");
}

async function displayUserIncomeDoughnut(){
    let ctx = $("#incomeCategoriesChart").get(0).getContext("2d");
    let fetchedData = await getDataFromUrl("income_category/");
    fetchedData = fetchedData.data;
    userIncomeDoughnut = doughNutChart(fetchedData, ctx, userIncomeDoughnut, "Income Categories");
}


function generateColors(numColors, startColor = 'rgba(75, 192, 192, 1)') {
    const colors = [];
    const [r, g, b] = startColor.match(/\d+/g).map(Number);

    for (let i = 0; i < numColors; i++) {
        const factor = i / numColors;
        const newR = Math.floor(r * (1 - factor) + 255 * factor);
        const newG = Math.floor(g * (1 - factor) + 255 * factor);
        const newB = Math.floor(b * (1 - factor) + 255 * factor);
        colors.push(`rgba(${newR}, ${newG}, ${newB}, 1)`);
    }

    return colors;
}

function doughNutChart(fetchedData, ctx, chartVariable, label){
    destroyChart(chartVariable);
    labels = Object.keys(fetchedData.amount);
    values = Object.values(fetchedData.amount);
    percentage = Object.values(fetchedData.percentage)
    for (let i = 0; i < labels.length; i++){
        const orignalLabel = labels[i];
        const percent = Math.round((percentage[i] * 100 + Number.EPSILON) * 100) / 100;
        labels[i] = orignalLabel + " (" + percent + "%)";
    }
    const data = {
        labels: labels,
        datasets: [{
          label: label,
          data: values,
          backgroundColor: generateColors(labels.length),
          hoverOffset: 4
        }]
    };
    return new Chart(ctx, doughnutConfig(data));
}

async function displayUserSavingGoal(){
    let ctx = $("#savingGoalChart").get(0).getContext("2d");
    let fetchedData = await getDataFromUrl("saving_goal/");
    let current = fetchedData.current;
    let goal = fetchedData.goal; 
    let percentage = Math.round((fetchedData.percentage * 100 + Number.EPSILON) * 100) / 100;
    let remainingPercentage = 100 - percentage;
    destroyChart(savingGoalChart);
    let labels = ["Saved (" + percentage + "%)", "Remaining (" + remainingPercentage+ "%)"];
    const data = {
        labels: labels,
        datasets: [{
          label: "Saving Goal",
          data: [current, goal - current],
          backgroundColor: generateColors(labels.length),
          hoverOffset: 4
        }]
    };
    savingGoalChart = new Chart(ctx, doughnutConfig(data));
    
} 

displayUserExpenseDoughnut();
displayUserIncomeDoughnut();
displayUserSavingGoal();

populateIncomeChart();
populateExpenseChart();