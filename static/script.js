import { addButtonSourcesHandler } from './buttonSourcesHandler.js';



export function runScript() {
    document.getElementById("resultText").innerHTML = `<div class='result-defaultText'><p>Мы активно собираем новости, группируем их и создаем удобные новостные сводки для вас.<br>Пожалуйста, подождите немного, чтобы мы смогли предоставить вам самую актуальную информацию.<br>Спасибо за ваше терпение!</p><p><img src="/static/images/loading.gif" width="100"></p></div>`;


    window.scrollTo({ top: 0, behavior: "smooth" });
    var itemList = document.getElementById("itemList");
    var checkboxes = itemList.querySelectorAll('input[type="checkbox"]:checked');
    var selectedItems = Array.from(checkboxes).map(function(checkbox) {
        return checkbox.value;
    });

    var selectedDate = document.getElementById("dateInput").value;

    var formData = new FormData();
    formData.append('items', selectedItems);
    formData.append('date', selectedDate);

    fetch('/run-script', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById("resultText").innerHTML = data;
        
        localStorage.setItem('selectedDate', selectedDate);
        localStorage.setItem('selectedItems', JSON.stringify(selectedItems));
        localStorage.setItem('resultText', data);
        // Вызываем функцию создани обработчиков кнопки "Показать источники"
        addButtonSourcesHandler();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
