import { useState } from "react";

export default function App() {
    const [tasks, setTasks] = useState([]);
    const [taskTitle, setTaskTitle] = useState("");

    function addTask() {
        if (!taskTitle.trim()) {
            return;
        }

        const newTask = {
            id: Date.now(),
            title: taskTitle,
            completed: false
        };

        setTasks([...tasks, newTask]);
        setTaskTitle("");
    }

    return (
        <main>
            <h1>Sample Task Tracker</h1>

            <section>
                <input
                    value={taskTitle}
                    onChange={(event) => setTaskTitle(event.target.value)}
                    placeholder="Add a task"
                />

                <button onClick={addTask}>Add Task</button>
            </section>

            <ul>
                {tasks.map((task) => (
                    <li key={task.id}>{task.title}</li>
                ))}
            </ul>
        </main>
    );
}