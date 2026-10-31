document.addEventListener('DOMContentLoaded', () => {
  const studentSelect = document.getElementById('student-select');
  const studentList = document.getElementById('student-list');
  const loginForm = document.getElementById('login-form');
  const studentDashboard = document.getElementById('student-dashboard');
  const adminDashboard = document.getElementById('admin-dashboard');

  let data = null;

  const renderStudentList = (students) => {
    studentList.innerHTML = '';
    students.forEach((student) => {
      const item = document.createElement('a');
      item.href = '#student-dashboard';
      item.className = 'student-item';
      item.innerHTML = `
        <strong>${student.full_name}</strong>
        <span>${student.email}</span>
      `;
      item.addEventListener('click', (event) => {
        event.preventDefault();
        showStudentDashboard(student.email);
      });
      studentList.appendChild(item);
    });
  };

  const renderSelectOptions = (students) => {
    studentSelect.innerHTML = students
      .map((student) => `<option value="${student.email}">${student.email}</option>`)
      .join('');
  };

  const renderAlerts = (alerts) => {
    const alertsList = document.getElementById('alerts-list');
    alertsList.innerHTML = alerts
      .map(
        (alert) => `
          <div class="alert-item severity-${alert.severity}">
            <h4>${alert.title}</h4>
            <div class="meta">${alert.category} • ${alert.severity.toUpperCase()}</div>
            <p>${alert.description}</p>
          </div>
        `
      )
      .join('');
  };

  const renderStudentDashboard = (student) => {
    document.getElementById('student-name').textContent = student.full_name;
    document.getElementById('student-email').textContent = student.email;
    document.getElementById('student-phone').textContent = student.phone_number;
    document.getElementById('student-faculty').textContent = student.faculty;
    document.getElementById('student-year').textContent = student.year_of_study;
    document.getElementById('student-device').textContent = student.device_id;

    document.getElementById('location-text').textContent = `Latitude: ${student.latitude}, Longitude: ${student.longitude}. Last updated: ${student.last_updated}`;

    const contactsList = document.getElementById('contacts-list');
    contactsList.innerHTML = `
      <div class="contact-item">
        <strong>Guardian Contact</strong><br />
        Parent<br />
        ${student.phone_number}
      </div>
    `;

    renderAlerts(data.alerts);
    studentDashboard.classList.remove('hidden');
    adminDashboard.classList.remove('hidden');
    studentDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const showStudentDashboard = (email) => {
    const student = data.students.find((item) => item.email === email);
    if (student) {
      renderStudentDashboard(student);
    }
  };

  const renderAdminDashboard = () => {
    const students = data.students;
    const alerts = data.alerts;

    document.getElementById('stat-students').textContent = students.length;
    document.getElementById('stat-alerts').textContent = alerts.length;
    document.getElementById('stat-risk').textContent = alerts.filter((alert) => alert.severity === 'high').length;

    const tableBody = document.getElementById('student-table-body');
    tableBody.innerHTML = students
      .map(
        (student) => `
          <tr>
            <td>${student.full_name}</td>
            <td>${student.email}</td>
            <td>${student.faculty}</td>
            <td>${student.phone_number}</td>
            <td>${student.latitude || 'N/A'}, ${student.longitude || 'N/A'}</td>
          </tr>
        `
      )
      .join('');
  };

  loginForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const selectedEmail = studentSelect.value;
    showStudentDashboard(selectedEmail);
  });

  fetch('./data/sample_data.json')
    .then((response) => response.json())
    .then((json) => {
      data = json;
      renderSelectOptions(json.students);
      renderStudentList(json.students);
      renderAdminDashboard();
      showStudentDashboard(json.students[0].email);
    })
    .catch((error) => {
      console.error('Failed to load data:', error);
      alert('Could not load prototype data.');
    });
});
