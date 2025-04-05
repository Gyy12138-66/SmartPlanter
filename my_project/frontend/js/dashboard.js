// dashboard.js

// const userId = localStorage.getItem('user_id');
//     if (!userId) {
//       alert('You must log in first!');
//       window.location.href = '/auth.html';
//     } else {
//       document.getElementById('welcome').textContent = `Welcome, User #${userId}!`;
//     }

// ✅ 临时绕过登录，仅供开发调试使用
const userId = localStorage.getItem('user_id') || 'test-user';
const welcomeElement = document.getElementById('welcome');
welcomeElement.textContent = `Welcome, User #${userId}!`;

// 🚪 登出功能
function logout() {
  localStorage.removeItem('user_id');
  window.location.href = '/auth.html';
}

// 🛠️ 你可以在这里添加将来获取数据库信息的 fetch 请求，例如：
const endpoints = [
    { id: 'light-data', name: 'Light Intensity', url: '/light_intensity', field: 'light_value' },
    { id: 'air-humidity-data', name: 'Air Humidity', url: '/air_humidity', field: 'humidity_value' },
    { id: 'air-temp-data', name: 'Air Temperature', url: '/air_temperature', field: 'temperature_value' },
    { id: 'soil-moisture-data', name: 'Soil Moisture', url: '/soil_moisture', field: 'moisture_value' }
  ];
  
  endpoints.forEach(sensor => {
    fetch(`http://localhost:8080${sensor.url}`)
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById(sensor.id);
        if (!container) return;
        container.innerHTML = `<strong>${sensor.name}:</strong><br>` +
          data.slice(0, 5).map(row => `${row[sensor.field]} (at ${row.measured_at})`).join('<br>');
      })
      .catch(err => {
        console.error(`Failed to load ${sensor.name}`, err);
      });
  });