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
