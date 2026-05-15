document.addEventListener("DOMContentLoaded", () => {
  let index = 0;
  const slides = document.querySelector('.slides');
  const totalSlides = document.querySelectorAll('.slides img').length;

  document.querySelector('.apres').addEventListener('click', () => {
    index++;
    if (index >= totalSlides) index = 0;
    updateSlide();
  });

  document.querySelector('.avant').addEventListener('click', () => {
    index--;
    if (index < 0) index = totalSlides - 1;
    updateSlide();
  });

  function updateSlide() {
    slides.style.transform = `translateX(-${index * 100}%)`;
  }

});