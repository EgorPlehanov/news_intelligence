const fs = require('fs');

// Функция для выбора случайного элемента из массива
function getRandomItem(array) {
  return array[Math.floor(Math.random() * array.length)];
}

// Функция для разделения текста на предложения и вставки тега <br> между предложениями
function addLineBreaks(text) {
  const sentences = text.split(/(?<=[.!?])\s+/); // Разделение текста на предложения
  return sentences.join("<br>"); // Объединение предложений с вставкой <br>
}

// Функция для генерации текста
export function getRandomLoadingText() {
  const data = fs.readFileSync('data.json', 'utf8');

  try {
    const jsonData = JSON.parse(data);

    // Выбор случайного сообщения и факта
    const randomMessage = getRandomItem(jsonData.messages);
    const randomFact = getRandomItem(jsonData.facts);

    // Добавление тега <br> между предложениями в сообщении и факте
    const formattedMessage = addLineBreaks(randomMessage.text);
    const formattedFact = addLineBreaks(randomFact.text);

    // Создание итогового текста
    const text = `<div class='result-defaultText'><p>${formattedMessage}<br><br>Интересный факт:<br>${formattedFact}</p><p><img src="/static/images/loading.gif" width="100"></p></div>`;
    return text;
  } catch (error) {
    console.error('Ошибка парсинга JSON:', error);
    return `<div class='result-defaultText'><p>Мы активно собираем новости, группируем их и создаем удобные новостные сводки для вас. Пожалуйста, подождите немного, чтобы мы смогли предоставить вам самую актуальную информацию. Спасибо за ваше терпение!</p><p><img src="/static/images/loading.gif" width="100"></p></div>`;
  }
}