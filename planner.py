import streamlit as st
import pandas as pd

# Load the provided CSV files to inspect their structure
meals_df = pd.read_csv('static/csv/recipe-ingredient.csv')
recipes_df = pd.read_csv('static/csv/recipe-ingredient.csv')

# Display the first few rows of each dataframe to understand their structure
meals_df_head = meals_df.head()
recipes_df_head = recipes_df.head()

# Function to calculate the total portions for a meal
def calculate_total_portions(days, eaters):
    # Portion sizes per person per day
    portions = {'Simon': 1, 'Maiia': 0.7, 'Both': 1.7}

    # Calculate total portions for the meal
    total_portions = sum([portions[eater] for eater in eaters]) * len(days)
    return total_portions

# Function to generate the shopping list
def generate_shopping_list(selected_meals, total_portions, recipes_df):
    shopping_list = {}

    # Iterate over each selected meal
    for meal in selected_meals:
        # Filter the recipes_df for the current meal
        meal_ingredients = recipes_df[recipes_df['recipe_name'] == meal]

        # Calculate the required amount for each ingredient
        for _, row in meal_ingredients.iterrows():
            ingredient = row['ingredient']
            amount = row['unit_amount'] * total_portions

            # Add to the shopping list
            if ingredient in shopping_list:
                shopping_list[ingredient] += amount
            else:
                shopping_list[ingredient] = amount

    # Convert the shopping list to a DataFrame
    shopping_list_df = pd.DataFrame(list(shopping_list.items()), columns=['Ingredient', 'Amount'])
    return shopping_list_df

# Streamlit App
def meal_planner_app():
    st.title("Meal Planner")

    # Step 1: Day Selection
    st.subheader("Select the days for which you want to cook:")
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    selected_days = st.multiselect("Days", days)

    # Step 2: Meal Selection
    st.subheader("Select Meals:")
    meal_times = ["breakfast", "lunch", "snack", "I. dinner", "II. dinner"]
    selected_meals = {meal_time: st.selectbox(f"{meal_time.capitalize()}", meals_df['recipe_name'].unique()) 
                      for meal_time in meal_times}

    # Step 3: People Selection
    st.subheader("Select who will be eating:")
    eaters_options = ["Simon", "Maiia", "Both"]
    selected_eaters = {meal_time: st.selectbox(f"Eaters for {meal_time.capitalize()}", eaters_options)
                       for meal_time in meal_times}

    # Step 4: Calculate Portions and Generate Shopping List
    if st.button("Generate Shopping List"):
        shopping_list = pd.DataFrame()
        for meal_time, meal in selected_meals.items():
            total_portions = calculate_total_portions(selected_days, [selected_eaters[meal_time]])
            meal_shopping_list = generate_shopping_list([meal], total_portions, recipes_df)
            shopping_list = pd.concat([shopping_list, meal_shopping_list])

        # Display the shopping list
        st.subheader("Shopping List:")
        st.write(shopping_list.groupby('Ingredient').sum().reset_index())


meal_planner_app()