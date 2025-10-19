const refreshButton = document.getElementById("refresh-btn");
const lastUpdated = document.getElementById("last-updated");
const runsContainer = document.getElementById("runs-container");

async function fetchRuns() {
    const response = await fetch("/api/runs");
    if (!response.ok) {
        throw new Error("Failed to fetch runs");
    }
    return response.json();
}

function renderRuns(data) {
    const runs = data.runs || [];
    if (runs.length === 0) {
        runsContainer.innerHTML = "<p>No runs detected yet. Execute the SBAR chaos harness to populate this dashboard.</p>";
        return;
    }

    const grouped = runs.reduce((acc, run) => {
        if (!acc[run.scene]) acc[run.scene] = [];
        acc[run.scene].push(run);
        return acc;
    }, {});

    const fragment = document.createDocumentFragment();

    Object.entries(grouped).forEach(([scene, entries]) => {
        const block = document.createElement("div");
        block.className = "scene-block";

        const heading = document.createElement("h2");
        heading.textContent = scene;
        block.appendChild(heading);

        const table = document.createElement("table");
        const thead = document.createElement("thead");
        thead.innerHTML = `
            <tr>
                <th>Timestamp</th>
                <th>Tokens</th>
                <th>Latency (s)</th>
                <th>Snapshots</th>
                <th>LLM</th>
                <th>Files</th>
            </tr>`;
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        entries.forEach(entry => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${entry.run}</td>
                <td>${entry.tokens}</td>
                <td>${entry.latency.toFixed(3)}</td>
                <td>${entry.snapshots}</td>
                <td>${entry.with_llm ? "✅" : "❌"}</td>
                <td>
                    <a href="${entry.summary}" target="_blank">summary.md</a>
                    <a href="${entry.progress}" target="_blank">progress.md</a>
                </td>`;
            tbody.appendChild(row);
        });
        table.appendChild(tbody);
        block.appendChild(table);
        fragment.appendChild(block);
    });

    runsContainer.innerHTML = "";
    runsContainer.appendChild(fragment);
}

async function refreshRuns() {
    try {
        const data = await fetchRuns();
        renderRuns(data);
        lastUpdated.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
    } catch (error) {
        console.error(error);
        lastUpdated.textContent = "Last updated: error fetching data";
    }
}

if (refreshButton) {
    refreshButton.addEventListener("click", refreshRuns);
}

refreshRuns();
