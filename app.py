from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    with sqlite3.connect('goals.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target INTEGER NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0
            )
        ''')
    conn.close()

@app.route('/')
def home():
    with sqlite3.connect('goals.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM goals')
        goals = cur.fetchall()
        # Sort goals: unfinished goals first
        goals.sort(key=lambda x: (x[3] >= x[2], x[0]))  # Sort by progress >= target, then by ID
    return render_template('index.html', goals=goals)

@app.route('/add_goal', methods=['POST'])
def add_goal():
    goal_name = request.form['goal_name']
    goal_target = int(request.form['goal_target'])
    with sqlite3.connect('goals.db') as conn:
        conn.execute('INSERT INTO goals (name, target) VALUES (?, ?)', (goal_name, goal_target))
    return redirect(url_for('home'))

@app.route('/update_progress/<int:goal_id>', methods=['POST'])
def update_progress(goal_id):
    increment_value = request.form.get('increment_value', default=1)  # Default to 1 if not provided
    increment_value = int(increment_value) if increment_value else 1  # Convert to integer or default to 1
    
    with sqlite3.connect('goals.db') as conn:
        # Update progress with the increment value
        conn.execute('UPDATE goals SET progress = progress + ? WHERE id = ?', (increment_value, goal_id))
        # Check if the goal is completed
        cur = conn.cursor()
        cur.execute('SELECT target, progress FROM goals WHERE id = ?', (goal_id,))
        target, progress = cur.fetchone()
        if progress >= target:
            pass  # Optionally handle completion
    return redirect(url_for('home'))

@app.route('/delete_goal/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    with sqlite3.connect('goals.db') as conn:
        conn.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)