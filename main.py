import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI()

dayMin = 1 # monday
dayMax = 7 # sunday
hourMin = 8 # 8:00
hourMax = 20 # 22:00

model_timewise = joblib.load('./data/pool_model02_.pkl') # contains days & hours

# endpoint to determine parameters and safety using a specific day and hour
@app.get("/parameters/predict/{day}/{hour}")
async def predict(day: int,hour: int):
    input_features = pd.DataFrame({'Day': [day], 'Hour': [hour]})
    
    predictions = model_timewise.predict(input_features)
    
    predicted_values = {
        'pH': float(predictions[0][0]),
        'Chlorine': float(predictions[0][1]),
        'Turbidity': float(predictions[0][2]),
        'Safety': int(predictions[0][3])
    }
    
    return predicted_values

# endpoint to predict the next time the pool will need maintainance
@app.get("/maintainance/predict/{today}/{hour_now}")
async def predict(today:int,hour_now:int):
    input_features = pd.DataFrame({'Day': [today], 'Hour': [hour_now]})
    next_maintainace_hour = 0
    next_maintainace_day = 0
    found = False
    startIndex01 = today
    startIndex02 = hour_now
           
    for day in range(startIndex01, dayMax+1):
        for hour in range(startIndex02, hourMax+1):
            input_features = pd.DataFrame({'Day': [day], 'Hour': [hour]})
            predictions = model_timewise.predict(input_features)
            
            safety_status = int(predictions[0][3])
            if safety_status == 0 :
                next_maintainace_day = day
                next_maintainace_hour = hour
                found = True
                break
            
            if hour == hourMax :
                hour = hourMin
                startIndex02 = hourMin
                print("hehe")                
            
        if found:
            break
        
        if day == dayMax :
            day = dayMin
            startIndex01 = dayMin
    
    if next_maintainace_day == 0 or next_maintainace_hour == 0 :
        return {"error": "Valid prediction not found for the provided inputs"}
    
    dif_day = next_maintainace_day - today
    dif_hour = next_maintainace_hour - hour_now
    
    forecast = { 'day': abs(dif_day), 'hour' : abs(dif_hour) }
    
    return forecast
            
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)         
    
