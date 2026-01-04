import React, { useEffect, useState } from 'react'
import Papa from 'papaparse'
import './styles.css'

const MEAL_TIMES = ['breakfast', 'lunch', 'snack', 'I. dinner', 'II. dinner']
const SIMON_MAIIA = 'Šimon a Maiia'
const SIMON = 'Šimon'
const MAIIA_MULTIPLIER = 1.65
const SIMON_MULTIPLIER = 1.0

export default function App() {
  const [mealsData, setMealsData] = useState([])
  const [ingredientsData, setIngredientsData] = useState([])
  const [cookingFor, setCookingFor] = useState(SIMON_MAIIA)
  const [weekend, setWeekend] = useState(false)
  const [mealAmounts, setMealAmounts] = useState([4,4,4,4,4])
  const [selection, setSelection] = useState({})
  const [chosenRecipesPortions, setChosenRecipesPortions] = useState(null)
  const [shoppingList, setShoppingList] = useState(null)

  useEffect(() => {
    async function load() {
      const kcalRes = await fetch('/static/csv/recipe-kcal.csv')
      const kcalText = await kcalRes.text()
      const kcalParsed = Papa.parse(kcalText, { header: true, skipEmptyLines: true })

      const ingRes = await fetch('/static/csv/recipe-ingredient.csv')
      const ingText = await ingRes.text()
      const ingParsed = Papa.parse(ingText, { header: true, skipEmptyLines: true })

      setMealsData(kcalParsed.data)
      setIngredientsData(ingParsed.data.map(r => ({
        ...r,
        unit_amount: r.unit_amount === undefined || r.unit_amount === '' ? null : Number(r.unit_amount),
        alternative_amount: r.alternative_amount === undefined || r.alternative_amount === '' ? null : Number(r.alternative_amount)
      })))
    }
    load()
  }, [])

  useEffect(() => {
    const defaultAmount = weekend ? 2 : 4
    setMealAmounts([defaultAmount, defaultAmount, defaultAmount, defaultAmount, defaultAmount])
  }, [weekend])

  function mealOptionsFor(mealTime) {
    const lower = mealTime.toLowerCase()
    const opts = mealsData.filter(m => m.meal && m.meal.toLowerCase() === lower).map(m => m.recipe_name)
    return ['None', ...opts]
  }

  function handleAmountChange(i, value) {
    const copy = [...mealAmounts]
    copy[i] = Number(value)
    setMealAmounts(copy)
  }

  function handleRandomize() {
    const newSelection = { ...selection }
    const newAmounts = [...mealAmounts]
    MEAL_TIMES.forEach((mt, i) => {
      const opts = mealOptionsFor(mt).slice(1)
      if (opts.length > 0) {
        newSelection[mt] = opts[Math.floor(Math.random() * opts.length)]
        newAmounts[i] = 1
      }
    })
    setSelection(newSelection)
    setMealAmounts(newAmounts)
  }

  function handleGenerate() {
    const chosenRecipes = {}
    MEAL_TIMES.forEach((mt, i) => {
      const recipe = selection[mt]
      if (recipe && recipe !== 'None') {
        chosenRecipes[recipe] = (chosenRecipes[recipe] || 0) + (mealAmounts[i] || 0)
      }
    })
    setChosenRecipesPortions(chosenRecipes)

    const list = {}
    Object.entries(chosenRecipes).forEach(([recipe, portions]) => {
      const rows = ingredientsData.filter(r => r.recipe_name === recipe)
      rows.forEach(row => {
        const ingredient = row.ingredient
        let si = (row.unit_amount || 0) * portions * 1.1
        let alt = row.alternative_amount === null ? null : (row.alternative_amount || 0) * portions * 1.1

        if (cookingFor === SIMON_MAIIA) {
          si = si * MAIIA_MULTIPLIER
          if (alt !== null) alt = alt * MAIIA_MULTIPLIER
        } else if (cookingFor === SIMON) {
          si = si * SIMON_MULTIPLIER
          if (alt !== null) alt = alt * SIMON_MULTIPLIER
        }

        if (!list[ingredient]) list[ingredient] = { si: 0, si_unit: row.unit || '', alt: 0, alt_unit: row.alternative_unit || '' }
        list[ingredient].si += si
        if (alt !== null) list[ingredient].alt += alt
      })
    })

    const cleaned = Object.entries(list).map(([ing, val]) => ({
      ingredient: ing,
      si: val.si && !Number.isNaN(val.si) ? Math.round(val.si) : 'N/A',
      si_unit: val.si_unit || '',
      alt: val.alt && !Number.isNaN(val.alt) && val.alt !== 0 ? Math.round(val.alt) : 'N/A',
      alt_unit: val.alt_unit || ''
    }))

    setShoppingList(cleaned)
  }

  function downloadShoppingCSV() {
    if (!shoppingList || shoppingList.length === 0) return
    const headers = ['Ingredient','SI Amount','Alternative Amount']
    const rows = shoppingList.map(r => [
      `"${r.ingredient.replace(/"/g, '""') }"`,
      r.si === 'N/A' ? 'N/A' : `${r.si} ${r.si_unit}`,
      r.alt === 'N/A' ? 'N/A' : `${r.alt} ${r.alt_unit}`
    ])
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'shopping-list.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app">
      <h1>Meal Planner</h1>

      <div className="controls">
        <div>
          <label>Cooking for:</label>
          <div className="radio-group">
            <label>
              <input type="radio" checked={cookingFor === SIMON_MAIIA} onChange={() => setCookingFor(SIMON_MAIIA)} /> {SIMON_MAIIA}
            </label>
            <label>
              <input type="radio" checked={cookingFor === SIMON} onChange={() => setCookingFor(SIMON)} /> {SIMON}
            </label>
          </div>
        </div>

        <div>
          <label>
            <input type="checkbox" checked={weekend} onChange={e => setWeekend(e.target.checked)} /> Weekend
          </label>
        </div>

        <details>
          <summary>Amount</summary>
          <div className="amounts">
            {MEAL_TIMES.map((mt, i) => (
              <div key={mt} className="amount-row">
                <label>{mt}</label>
                <input type="range" min="0" max="7" value={mealAmounts[i]} onChange={e => handleAmountChange(i, e.target.value)} />
                <input type="number" min="0" max="7" value={mealAmounts[i]} onChange={e => handleAmountChange(i, e.target.value)} />
              </div>
            ))}
          </div>
        </details>

        <div className="actions">
          <button onClick={handleRandomize}>Random Selection</button>
          <button onClick={handleGenerate}>Make Shopping List for {cookingFor}</button>
          {shoppingList && (
            <button onClick={downloadShoppingCSV}>Download shopping-list.csv</button>
          )}
        </div>
      </div>

      <div className="selections">
        {MEAL_TIMES.map((mt, i) => (
          <div key={mt} className="selection-row">
            <label>{mt}</label>
            <select value={selection[mt] || 'None'} onChange={e => setSelection({ ...selection, [mt]: e.target.value })}>
              {mealOptionsFor(mt).map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
        ))}
      </div>

      {chosenRecipesPortions && (
        <div className="chosen">
          <h2>Chosen Recipes and Portions</h2>
          <ul>
            {Object.entries(chosenRecipesPortions).map(([r,p]) => <li key={r}>{r}: {p} portions</li>)}
          </ul>
        </div>
      )}

      {shoppingList && (
        <div className="shopping">
          <h2>Shopping List for {cookingFor}</h2>
          <table>
            <thead>
              <tr><th>Ingredient</th><th>SI Amount</th><th>Alternative Amount</th></tr>
            </thead>
            <tbody>
              {shoppingList.map(row => (
                <tr key={row.ingredient}>
                  <td>{row.ingredient}</td>
                  <td>{row.si === 'N/A' ? 'N/A' : `${row.si} ${row.si_unit}`}</td>
                  <td>{row.alt === 'N/A' ? 'N/A' : `${row.alt} ${row.alt_unit}`}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <footer>
        <p>Static CSVs are loaded from /static/csv. To deploy on Vercel, push this repo — Vercel will run npm install and build automatically.</p>
      </footer>
    </div>
  )
}
