function setup_field_groups() {
  const max_fields = 10;
  const $add_button = $('#addButton');
  const $filterFields = $('.filter_field');

  const $filters_filled_at_load = $filterFields.children('.value_field').filter(function () {
    return this.value;
  }).parent();

  // The number of VISIBLE filter fields
  let number_of_fields = $filterFields.index($filters_filled_at_load.last()) + 2;
  $filterFields.slice(0, number_of_fields).removeClass('d-none').change();

  $add_button.click(function (e) {
    e.preventDefault();

    if (number_of_fields < max_fields) {
      $filterFields.eq(number_of_fields).removeClass('d-none');
      number_of_fields++;
    } else {
      alert('Maximale Anzahl Felder erreicht');
    }
  });
}

function update_operations() {
  /**
   * For $(this) attribute selector, change the sibling operation selector to only include allowed operations.
   */
  const allowed_operations = $(this).find("option:selected").data('operations').split(",");
  const $group = $(this).parent('.filter_field');
  $group.find('.operation_field option').each(function () {
    const operation = $(this).val();
    if (allowed_operations.includes(operation)) {
      $(this).removeClass('d-none');
      $(this).attr('disabled', false);
    } else {
      $(this).addClass('d-none');
      $(this).attr('disabled', true);
    }
  });

  // Switch current selection if necessary
  const current_operation = $group.find('.operation_field option:selected').val();
  if (!allowed_operations.includes(current_operation)) {
    $group.find('.operation_field').val(allowed_operations[0]);
  }
}

$(function () {

  setup_field_groups();
  $('.attribute_field').change(update_operations);
  $('.attribute_field:visible').change();

});