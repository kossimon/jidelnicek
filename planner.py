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
    expander_sliders = st.expander("Amount")
    with expander_sliders:
        # Step 1: Slider for Meal Amounts
        st.subheader("Select the amount of each meal:")
        meal_times = ["breakfast", "lunch", "snack", "I. dinner", "II. dinner"]
        meal_amounts = [st.slider(f"Amount of {meal}", min_value=0, max_value=7, value=4) for meal in meal_times]

    # Step 2: Random Selection Button
    if st.button("Random Selection"):
        for i, meal_time in enumerate(meal_times):
            default_key = f"default_{meal_time}"
            meal_options = ['None'] + meals_df[meals_df['meal'].str.lower() == meal_time.lower()]['recipe_name'].tolist()
            st.session_state[default_key] = random.choice(meal_options[1:])
            meal_amounts[i] = 1

    # Step 3: Display Meals
    for i, meal_time in enumerate(meal_times):
        st.subheader(f"Meals to cook for {meal_time.capitalize()}")
        meal_options = ['None'] + meals_df[meals_df['meal'].str.lower() == meal_time.lower()]['recipe_name'].tolist()

        default_key = f"default_{meal_time}"
        if default_key not in st.session_state:
            st.session_state[default_key] = 'None'

        default_option = st.session_state[default_key]
        chosen_recipe = st.selectbox(f"{meal_time.capitalize()}", meal_options, index=meal_options.index(default_option))
        st.session_state[default_key] = chosen_recipe

    # Step 4: Generate Shopping List
    if st.button("Make Shopping List"):
        # Find the recipes chosen for each meal
        chosen_recipes = {}
        for i, meal_time in enumerate(meal_times):
            chosen_recipe = st.session_state[f"default_{meal_time}"]
            if chosen_recipe and chosen_recipe != 'None':
                chosen_recipes.setdefault(chosen_recipe, 0)
                chosen_recipes[chosen_recipe] += meal_amounts[i]

        # List all chosen recipes and the number of portions for each
        st.subheader("Chosen Recipes and Portions")
        for recipe, portions in chosen_recipes.items():
            st.write(f"{recipe}: {portions} portions")

            # Show the amounts to use in the recipe
            recipe_ingredients = recipes_df[recipes_df['recipe_name'] == recipe]
            data = []
            for _, row in recipe_ingredients.iterrows():
                ingredient = row['ingredient']
                si_amount = round(row['unit_amount'] * portions * 1.1, 2)
                alt_amount = "N/A" if row['alternative_amount'] == "N/A" else round(float(row['alternative_amount']) * portions * 1.1, 2)
                
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
                si_amount = round(row['unit_amount'] * portions * 1.1, 2)
                alt_amount = "N/A" if row['alternative_amount'] == "N/A" else round(float(row['alternative_amount']) * portions * 1.1, 2)
                
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
