import streamlit as st
import pandas as pd
import random

# Load the data
meals_df = pd.read_csv('static/csv/recipe-kcal.csv')
recipes_df = pd.read_csv('static/csv/recipe-ingredient.csv')
recipes_df["alternative_amount"].fillna("N/A", inplace=True)
recipes_df["alternative_unit"].fillna("N/A", inplace=True)

def main():
    st.title("Meal Planner")

    # User selects the days they want to cook
    st.subheader("Select the days you want to cook:")
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    # Display checkboxes for each day in a single row
    day_columns = st.columns(len(days))
    selected_days = [day_columns[i].checkbox(day, value=False, key=day) for i, day in enumerate(days)]

    # Setup for meal time and meal preferences
    meal_times = ["breakfast", "lunch", "snack", "I. dinner", "II. dinner"]
    meal_preferences = ["Maiia", "Simon", "Both"]

    # Loop through each day to set up meal selections
    for i, day in enumerate(days):
        if selected_days[i]:
            st.subheader(f"Meals to cook on {day}")
            columns = st.columns(len(meal_times))

            for j, meal_time in enumerate(meal_times):
                with columns[j]:
                    # Meal options based on time of the day
                    meal_options = ['None'] + meals_df[meals_df['meal'].str.lower() == meal_time.lower()]['recipe_name'].tolist()
                    
                    # Selection of the meal
                    default_key = f"default_{day}_{meal_time}"
                    if default_key not in st.session_state:
                        st.session_state[default_key] = random.choice(meal_options[1:])
                    
                    default_option = st.session_state[default_key]
                    selected_meal = st.selectbox(f"{meal_time}", meal_options, index=meal_options.index(default_option), key=f"{day}_{meal_time}")

                    # Selection for who will eat the meal
                    preference_key = f"preference_{day}_{meal_time}"
                    if preference_key not in st.session_state:
                        st.session_state[preference_key] = "Both"
                    st.radio("Who will eat?", meal_preferences, key=preference_key)

    # Process to create a shopping list based on selected meals
    if st.button("Make Shopping List"):
        chosen_recipes = {}

        # Determine portions needed for each selected day
        for i, day in enumerate(days):
            if selected_days[i]:
                portions = 1  # Assign one portion per selected day

                for meal_time in meal_times:
                    chosen_recipe = st.session_state.get(f"{day}_{meal_time}")
                    preference = st.session_state.get(f"preference_{day}_{meal_time}", "Both")
                    eaters = 2 if preference == "Both" else 1
                    if chosen_recipe and chosen_recipe != 'None':
                        chosen_recipes.setdefault(chosen_recipe, 0)
                        chosen_recipes[chosen_recipe] += portions * eaters

        # Display chosen recipes and calculate ingredients needed
        for recipe, portions in chosen_recipes.items():
            st.write(f"{recipe}: {portions} portions")

            recipe_ingredients = recipes_df[recipes_df['recipe_name'] == recipe]
            data = []
            for _, row in recipe_ingredients.iterrows():
                ingredient = row['ingredient']
                amount = round(row['unit_amount'] * portions, 2)
                data.append([ingredient, f'{amount} {row["unit"]}'])

            df = pd.DataFrame(data, columns=['Ingredient', 'Amount'])
            st.table(df)

        # Generate the shopping list
        shopping_list = {}
        for recipe, portions in chosen_recipes.items():
            recipe_ingredients = recipes_df[recipes_df['recipe_name'] == recipe]
            for _, row in recipe_ingredients.iterrows():
                ingredient = row['ingredient']
                amount = round(row['unit_amount'] * portions, 2)
                shopping_list.setdefault(ingredient, 0)
                shopping_list[ingredient] += amount

        st.subheader("Shopping List")
        data = []
        for ingredient, amount in shopping_list.items():
            data.append([ingredient, f'{round(amount, 2)} {recipes_df[recipes_df["ingredient"] == ingredient]["unit"].iloc[0]}'])

        df = pd.DataFrame(data, columns=['Ingredient', 'Total Amount'])
        st.table(df)

if __name__ == "__main__":
    main()
