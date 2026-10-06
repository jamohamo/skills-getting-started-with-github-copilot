document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activityOptions = document.getElementById("activity-options");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities", { cache: "no-store" });
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activityOptions.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants:</strong>
            <ul class="participants-list">
              ${
                details.participants.length
                  ? details.participants.map(
                      (email) => `
                        <li class="participant-item">
                          <span>${email}</span>
                          <button
                            type="button"
                            class="delete-participant-btn"
                            data-activity="${name}"
                            data-email="${email}"
                            aria-label="Remove participant from activity"
                            title="Remove participant from activity"
                          >
                            ✕
                          </button>
                        </li>
                      `
                    ).join("")
                  : "<li class='empty-participants'>No participants yet.</li>"
              }
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const optionLabel = document.createElement("label");
        optionLabel.className = "activity-option";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "activity_names";
        checkbox.value = name;

        const optionName = document.createElement("span");
        optionName.textContent = name;

        optionLabel.append(checkbox, optionName);
        activityOptions.appendChild(optionLabel);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  document.addEventListener("click", async (event) => {
    const deleteButton = event.target.closest(".delete-participant-btn");
    if (!deleteButton) {
      return;
    }

    const activity = deleteButton.dataset.activity;
    const email = deleteButton.dataset.email;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "Unable to unregister participant.";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister participant.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering participant:", error);
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activityNames = Array.from(
      activityOptions.querySelectorAll('input[name="activity_names"]:checked'),
      (checkbox) => checkbox.value
    );

    if (activityNames.length === 0) {
      messageDiv.textContent = "Select at least one activity.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      return;
    }

    try {
      const response = await fetch("/activities/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, activity_names: activityNames }),
      });

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
