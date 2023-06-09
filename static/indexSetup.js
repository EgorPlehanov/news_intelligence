import { runScript } from './script.js';
import { addButtonSourcesHandler } from './buttonSourcesHandler.js';



window.addEventListener('DOMContentLoaded', () => {
  const currentDate = new Date().toISOString().split('T')[0];
  const storedDate = localStorage.getItem('selectedDate');

  const dateInput = document.getElementById('dateInput');
  dateInput.setAttribute('max', currentDate);
  dateInput.value = storedDate || currentDate;

  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  const storedItems = localStorage.getItem('selectedItems');
  if (storedItems) {
    const selectedItems = JSON.parse(storedItems);
    checkboxes.forEach((checkbox) => {
      if (selectedItems.includes(checkbox.value)) {
        checkbox.checked = true;
      }
    });
  } else {
    checkboxes[0].checked = true;
  }

  const defaultResultText = `<div class='result-defaultText'>Выберите дату и источники,<br>затем нажмите на кнопку 'Создать сводку',<br>и здесь появится новостная сводка.</div>`;
  const storedResultText = localStorage.getItem('resultText');
  if (storedResultText) {
    document.getElementById("resultText").innerHTML = storedResultText;
    addButtonSourcesHandler();
  } else {
    document.getElementById("resultText").innerHTML = defaultResultText;
  }
});

// Rод для вызова функции runScript при клике на кнопку
document.getElementById("runButton").addEventListener("click", runScript);
