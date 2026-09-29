from fastapi import FastAPI, HTTPException
from datetime import date
import db_helper
from typing import List
from pydantic import BaseModel

app = FastAPI()

class Expense(BaseModel):
    amount: float
    category: str
    notes: str

class DateRange(BaseModel):
    start_date: date
    end_date: date



@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expense(expense_date: date):
    try:
        expenses = db_helper.fetch_expenses_for_date(expense_date)
        return expenses if expenses else []
    except Exception as e:
        print("ERROR FETCHING:", e)
        raise HTTPException(status_code=500, detail="Error fetching expenses")


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expense]):
    try:
        print("DATE:", expense_date)
        print("EXPENSES RECEIVED:", expenses)

        db_helper.delete_expenses_for_date(expense_date)

        for expense in expenses:
            db_helper.insert_expense(
                expense_date,
                float(expense.amount),
                expense.category.strip().upper(),
                expense.notes.strip()
            )

        return {"message": "Expenses updated successfully"}

    except Exception as e:
        print("ERROR INSERTING:", e)
        raise HTTPException(status_code=500, detail="Error updating expenses")

@app.post("/analytics/")
def get_analytics(date_range:DateRange):
    data=db_helper.fetch_data_summary(date_range.start_date,date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500,detail="failed to retreve expense summary from database")
    total=sum([row["total"] for row in data])
    breakdown={}
    for row in data:
        percentage=(row['total']/total)*100 if total !=0 else 0
        breakdown[row["category"]]={
            "total":row["total"],
            "percentage" : percentage
        }
    return breakdown