export function addButtonSourcesHandler() {
    const buttons = document.querySelectorAll('.show-sources-btn');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const currentBlock = button.closest('.news-block');
            const currentSourcesList = button.closest('.news-block').querySelector('.sources-list');
            const isOpen = currentSourcesList.classList.contains('show');

            // Закрыть другие открытые блоки
            const openBlocks = document.querySelectorAll('.news-block');
            openBlocks.forEach(openBlock => {
                if (openBlock !== currentBlock) {
                    const openSourcesList = openBlock.closest('.news-block').querySelector('.sources-list');
                    if (openSourcesList.classList.contains('show')) {
                        openSourcesList.style.maxHeight = '0';
                        openSourcesList.classList.remove('show');
                        const openButton = openBlock.querySelector('.show-sources-btn');
                        openButton.classList.remove('active');
                        openButton.textContent = 'Показать источники';
                    }
                }
            });

            // Открыть/закрыть текущий блок
            if (isOpen) {
                currentSourcesList.style.maxHeight = '0';
                currentSourcesList.classList.remove('show');
                button.classList.remove('active');
                button.textContent = 'Показать источники';
            } else {
                currentSourcesList.style.maxHeight = currentSourcesList.scrollHeight + 'px';
                currentSourcesList.classList.add('show');
                button.classList.add('active');
                button.textContent = 'Скрыть источники';
            }
        });
    });
}
