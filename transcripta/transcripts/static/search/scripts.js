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

function update_input_field() {
  /**
   * For $(this) attribute selector, change the sibling value field to be of the type suggested by the attribute.
   * The value is carried over, if possible in any way.
   */
  const template_name = $(this).find("option:selected").data('template-name');
  const $template = $('#'+template_name);
  const $value_field = $(this).parent('.filter_field').find('.value_field');
  const value_field_id = $value_field.attr('id');
  const value_field_name = $value_field.attr('name');
  const value_field_value = $value_field.val();
  const new_field = $template.clone();
  new_field.attr('id', value_field_id);
  new_field.attr('name', value_field_name);
  new_field.val(value_field_value);
  $value_field.replaceWith(new_field);
}

function hide_field_group() {
  /**
   * For $(this) attribute selector, reset and hide the parent field group.
   */
  const $group = $(this).parent('.filter_field');
  $group.addClass('d-none');
  // Reset to the default attribute and default operation
  const $attribute_field = $group.find('.attribute_field');
  $attribute_field.prop('selectedIndex', '0').change();
  const $operation_field = $group.find('.operation_field');
  $operation_field.prop('selectedIndex', '0');
  // Empty the value field if necessary
  $group.find('.value_field').val("");
}

$(function () {

  setup_field_groups();
  $('.attribute_field')
      .change(update_operations)
      .change(update_input_field);
  $('.attribute_field:visible').change();
  $('.removal_button').click(hide_field_group);

});