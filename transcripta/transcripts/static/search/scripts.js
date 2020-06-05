$(function() {

  const max_fields = 10;
  const $add_button = $('#addButton');
  const $filterFields = $('.filter_field');

  const $filters_filled_at_load = $filterFields.children('.value_field').filter(function() {
    return this.value;
  }).parent();

  // The number of VISIBLE filter fields
  let number_of_fields = $filterFields.index($filters_filled_at_load.last()) + 2;
  $filterFields.slice(0, number_of_fields).removeClass('d-none');

  $add_button.click(function (e) {
    e.preventDefault();

    if (number_of_fields < max_fields) {
      $filterFields.eq(number_of_fields).removeClass('d-none');
      number_of_fields++;
    } else {
      alert('Maximale Anzahl Felder erreicht');
    }
  });

});