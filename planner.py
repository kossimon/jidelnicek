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

    # Step 1: Slider and Dropdown for Meal Amounts and Selection
    st.subheader("Select the amount and recipe for each meal:")
    meal_times = ["breakfast", "lunch", "snack", "I. dinner", "II. dinner"]
    meal_amounts = [0] * len(meal_times)
    chosen_recipes = {}

    for i, meal_time in enumerate(meal_times):
        st.write(f"### {meal_time.capitalize()}")
        amount = st.slider(f"Amount of {meal_time}", min_value=0, max_value=7, value=3)
        meal_amounts[i] = amount

        meal_options = ['None'] + meals_df[meals_df['meal'].str.lower() == meal_time.lower()]['recipe_name'].tolist()
        chosen_recipe = st.selectbox(f"Select recipe for {meal_time}", meal_options)
        
        if chosen_recipe and chosen_recipe != 'None':
            chosen_recipes.setdefault(chosen_recipe, 0)
            chosen_recipes[chosen_recipe] += amount

    # Step 2: Random Selection Button
    if st.button("Random Selection"):
        for i, meal_time in enumerate(meal_times):
            meal_options = ['None'] + meals_df[meals_df['meal'].str.lower() == meal_time.lower()]['recipe_name'].tolist()
            chosen_recipe = random.choice(meal_options[1:])
            chosen_recipes.setdefault(chosen_recipe, 0)
            chosen_recipes[chosen_recipe] += 1

    # Step 3: Display Meals and Generate Shopping List
    st.subheader("Chosen Recipes and Portions")
    shopping_list = {}

    for recipe, portions in chosen_recipes.items():
        st.write(f"{recipe}: {portions} portions")
        recipe_ingredients = recipes_df[recipes_df['recipe_name'] == recipe]

        for _, row in recipe_ingredients.iterrows():
            ingredient = row['ingredient']
            si_amount = round(row['unit_amount'] * portions * 1.1, 2)
            alt_amount = "N/A" if row['alternative_amount'] == "N/A" else round(float(row['alternative_amount']) * portions, 2)

            if cooking_for_maiia:
                si_amount *= 1.72
                if alt_amount != "N/A":
                    alt_amount *= 1.72

            si_amount = round(si_amount, 0) if not pd.isna(si_amount) and si_amount != 0 else "N/A"
            alt_amount = round(alt_amount, 0) if alt_amount != "N/A" and alt_amount != 0 else "N/A"

            shopping_list.setdefault(ingredient, {'si': 0, 'alt': 0})
            shopping_list[ingredient]['si'] += si_amount
            if alt_amount != "N/A":
                shopping_list[ingredient]['alt'] += alt_amount

    # Step 4: Display Shopping List
    st.subheader("Shopping List")

    shopping_data = []
    for ingredient, amounts in shopping_list.items():
        si_amount = amounts['si']
        alt_amount = amounts['alt']
        
        si_amount = round(si_amount, 0) if si_amount != 0 else "N/A"
        alt_amount = round(alt_amount, 0) if alt_amount != 0 else "N/A"
        
        shopping_data.append([ingredient, f'{si_amount} g', f'{alt_amount}'])

    df_shopping = pd.DataFrame(shopping_data, columns=['Ingredient', 'Amount (g)', 'Alternative Amount'])
    st.table(df_shopping)


if __name__ == "__main__":
    main()
