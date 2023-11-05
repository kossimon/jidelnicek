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

    # Adding a checkbox for "Cooking for Maiia"
    cooking_for_maiia = st.checkbox("Cooking for Maiia", value=True)

    # Step 1: Day Selection
    st.subheader("Select days:")
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    # Arrange checkboxes in a single row
    day_columns = st.columns(len(days))
    selected_days = [day_columns[i].checkbox(day, key=day) for i, day in enumerate(days)]

    # Step 2: Meal Selection
    meal_times = ["breakfast", "lunch", "snack", "I. dinner", "II. dinner"]

    if st.button("Random Selection"):
        for day in days:
            for meal_time in meal_times:
                default_key = f"default_{day}_{meal_time}"
                meal_options = ['None'] + meals_df[meals_df['meal'].str.lower() == meal_time.lower()]['recipe_name'].tolist()
                st.session_state[default_key] = random.choice(meal_options[1:])

    for i, day in enumerate(days):
        if selected_days[i]:
            st.subheader(f"Meals to cook on {day}")

            # Create columns for each meal time
            columns = st.columns(len(meal_times))

            for j, meal_time in enumerate(meal_times):
                with columns[j]:
                    meal_options = ['None'] + meals_df[meals_df['meal'].str.lower() == meal_time.lower()]['recipe_name'].tolist()
                    
                    # Set a random default option only if it has not been set before
                    default_key = f"default_{day}_{meal_time}"
                    if default_key not in st.session_state:
                        st.session_state[default_key] = random.choice(meal_options[1:])
                    
                    default_option = st.session_state[default_key]
                    st.selectbox(f"{meal_time}", meal_options, index=meal_options.index(default_option), key=f"{day}_{meal_time}")


    # Step 3: Generate Shopping List
    if st.button("Make Shopping List"):
        # Find the recipes chosen for each day and mealtime
        chosen_recipes = {}
    
        # Calculate the number of selected days (this is the new logic)
        # No need to find the next cooking day anymore, just count the checked days
        selected_day_count = sum(selected_days)
    
        for i, day in enumerate(days):
            if selected_days[i]:
                # Now, instead of calculating portions based on the next cooking day,
                # simply use the number of selected days for portions
                portions = selected_day_count
    
                for meal_time in meal_times:
                    chosen_recipe = st.session_state.get(f"{day}_{meal_time}")
                    if chosen_recipe and chosen_recipe != 'None':
                        chosen_recipes.setdefault(chosen_recipe, 0)
                        chosen_recipes[chosen_recipe] += portions

        # List all chosen recipes and the number of portions for each
        st.subheader("Chosen Recipes and Portions")
        for recipe, portions in chosen_recipes.items():
            st.write(f"{recipe}: {portions} portions")

            # Show the amounts to use in the recipe
            recipe_ingredients = recipes_df[recipes_df['recipe_name'] == recipe]
            data = []
            for _, row in recipe_ingredients.iterrows():
                ingredient = row['ingredient']
                si_amount = round(row['unit_amount'] * portions, 2)
                alt_amount = "N/A" if row['alternative_amount'] == "N/A" else round(float(row['alternative_amount']) * portions, 2)
                
                # Applying the multiplier for "Cooking for Maiia"
                if cooking_for_maiia:
                    si_amount *= 1.72
                    if alt_amount != "N/A":
                        alt_amount = round(alt_amount * 1.72, 2)
                
                si_amount = round(si_amount, 0) if not pd.isna(si_amount) and si_amount != 0 else "N/A"
                alt_amount = round(alt_amount, 0) if alt_amount != "N/A" and alt_amount != 0 else "N/A"

                data.append([ingredient, f'{si_amount} {row["unit"]}', f'{alt_amount} {row["alternative_unit"]}'])

            df = pd.DataFrame(data, columns=['Ingredient', 'SI Amount', 'Alternative Amount'])
            df = df.replace('N/A N/A', "N/A").replace('N/A 0.0', "N/A").replace('N/A nan', "N/A").replace('0.0 nan', "N/A").replace('nan', "")
            st.table(df)

        # Generate the shopping list
        shopping_list = {}
        for recipe, portions in chosen_recipes.items():
            recipe_ingredients = recipes_df[recipes_df['recipe_name'] == recipe]
            for _, row in recipe_ingredients.iterrows():
                ingredient = row['ingredient']
                si_amount = round(row['unit_amount'] * portions, 2)
                alt_amount = "N/A" if row['alternative_amount'] == "N/A" else round(float(row['alternative_amount']) * portions, 2)
                
                # Applying the multiplier for "Cooking for Maiia"
                if cooking_for_maiia:
                    si_amount *= 1.72
                    if alt_amount != "N/A":
                        alt_amount = round(alt_amount * 1.72, 2)
                
                shopping_list.setdefault(ingredient, {'si': [0, row['unit']], 'alt': [0, row['alternative_unit']]})
                shopping_list[ingredient]['si'][0] += si_amount
                if alt_amount != "N/A":
                    shopping_list[ingredient]['alt'][0] += alt_amount

        # Display the shopping list
        st.subheader("Shopping List")
        
        data = []
        for ingredient, amounts in shopping_list.items():
            si_amount, si_unit = amounts['si']
            alt_amount, alt_unit = amounts['alt']
            
            si_amount = round(si_amount, 0) if not pd.isna(si_amount) and si_amount != 0 else "N/A"
            alt_amount = round(alt_amount, 0) if alt_amount != 0 else "N/A"
            
            data.append([ingredient, f'{si_amount} {si_unit}', f'{alt_amount} {alt_unit}'])


        df = pd.DataFrame(data, columns=['Ingredient', 'SI Amount', 'Alternative Amount'])
        df = df.replace('N/A N/A', "").replace('N/A',"").replace('N/A nan',"")
        st.table(df)


if __name__ == "__main__":
    main()


