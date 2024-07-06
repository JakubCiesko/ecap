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
async function extractDateAmount(url){
    let data = {"date": [], "amount": []};
    await getDataFromUrl(url)
    .then(urlData => {
        if (urlData && Object.keys(urlData)[0] != "error"){
            data.date = Object.values(urlData.date);
            data.amount = Object.values(urlData.amount);
        }
    });
    return data
}

async function getUserExpenses(){return extractDateAmount("/get_user_expenses")}
async function getUserIncomes(){return extractDateAmount("/get_user_incomes")}
async function getExpectedExpenses(){return extractDateAmount("/get_user_expected_expenses");}
async function getExpectedIncome(){return extractDateAmount("/get_user_expected_incomes")}
async function getUserTotalIncome(){return getDataFromUrl("/get_user_total_income");}
async function getUserTotalExpense(){return getDataFromUrl("/get_user_total_expense");}
async function getUserTotalBalance(){return getDataFromUrl("/get_user_total_balance");}
async function getUserSavingGoal(){return getDataFromUrl("/get_user_savings");}

/*
function renderSavingGoals(savingGoals) {
    const carouselInner = document.getElementById('carouselInner');
    let index = 0;
    savingGoals.forEach(savingGoal => {
        const isActive = index === 0 ? 'active' : '';
        index++;
        const carouselItem = document.createElement('div');
        carouselItem.classList.add('carousel-item', isActive);
        carouselItem.innerHTML = `
            <div class="bg-light rounded d-flex align-items-center justify-content-between p-4">
                <object data="/static/img/savings-hog.svg" type="image/svg+xml" class="svg-icon" width="48" height="48"></object>
                <div class="ms-3">
                    <p class="mb-2">${savingGoal.current}</p>
                    <h6 class="mb-0">${savingGoal.target}€</h6>
                </div>
            </div>
        `;
        carouselInner.appendChild(carouselItem);
    });
}*/


async function updateValues (){
    try {
        const [income, expense, balance, savings] = await Promise.all([
            getUserTotalIncome(), getUserTotalExpense(), getUserTotalBalance(), getUserSavingGoal()
        ]);
        document.getElementById("income").textContent = income.user_income;
        document.getElementById("expense").textContent = expense.user_expense;
        document.getElementById("balance").textContent = balance.user_balance;
        if (savings.saving_goals.length){
            document.getElementById("savings").textContent = savings.saving_goals[0].current + "/" + savings.saving_goals[0].target;
        }
    } catch (error) {
        console.error("Error updating values: ", error);
    }
}
updateValues();


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
                    reportTable.innerHTML = '';
                reports.reverse().forEach(report => {
                    const startDateFormatted = formatDate(report.start_date);
                    const endDateFormatted = formatDate(report.end_date);
                    const row = document.createElement('tr');
                    const checkboxCell = document.createElement('td');
                    checkboxCell.innerHTML = checkboxCell.innerHTML = '<input class="form-check-input" type="checkbox" name="selected_items" value="' + report.id + '">';
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
                    printCell.innerHTML = "<a class=\"btn btn-sm btn-primary\" href=\"report/" + report.id + " \" target=\"_blank\">Detail</a>";
                    row.appendChild(printCell);
                    reportTable.appendChild(row);
                })
            }
        } 
    )
}

displayUserReports();

function createUserReport(startDate, endDate){return getDataFromUrl("create_user_report/" + startDate + "/" + endDate);}

document.getElementById('selectAll').addEventListener('change', function() {
    var checkboxes = document.querySelectorAll('input[name="selected_items"]');
    for (var checkbox of checkboxes) {
        checkbox.checked = this.checked;
    }
});


document.getElementById('deleteSelected').addEventListener('click', function() {
    const selectedItems = [];
    const checkboxes = document.querySelectorAll('input[name="selected_items"]:checked');
    checkboxes.forEach(checkbox => {
        selectedItems.push(checkbox.value);
    });

    if (selectedItems.length > 0) {
        fetch('/delete_selected_reports/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Make sure to include CSRF token
            },
            body: JSON.stringify({ 'selected_items': selectedItems })
        })
        .then(response => {
            if (response.ok) {
                selectedItems.forEach(id => {
                    const row = document.querySelector(`input[value="${id}"]`).closest('tr');
                    row.remove();
                });
            } else {
                alert('Failed to delete selected reports.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the reports.');
        });
    } else {
        alert('No reports selected for deletion.');
    }
});

