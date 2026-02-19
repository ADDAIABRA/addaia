"use strict";

$(document).ready(function() {
  $("#myEvent").fullCalendar({
    height: 'auto',
    defaultView: 'agendaWeek',
    allDaySlot: false,
    slotDuration: '01:00:00',
    minTime: '00:00:00',
    maxTime: '23:59:59',
    locale: 'pt-br',
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'month,agendaWeek,agendaDay,listWeek'
    },
    editable: false,
    events: '/agendamentos/get-events/',
    
    // Al clicar en un espacio vazio
    dayClick: function(date, jsEvent, view) {
      const selectedDate = date.format('YYYY-MM-DDTHH:mm');
      $('#id_data_inicio').val(selectedDate);
      $('#modalAgendamento').modal('show');
    },

    // Ao clicar em um evento existente
    eventClick: function(calEvent, jsEvent, view) {
      alert('Agendamento: ' + calEvent.title + '\nResponsável: ' + calEvent.user);
    }
  });

  // Handle Form Submission
  $('#formAgendamento').on('submit', function(e) {
    e.preventDefault();
    const $btn = $('#btnSalvarAgendamento');
    $btn.addClass('btn-progress disabled');

    $.ajax({
      url: '/agendamentos/create/',
      type: 'POST',
      data: $(this).serialize(),
      success: function(response) {
        $btn.removeClass('btn-progress disabled');
        $('#modalAgendamento').modal('hide');
        $('#myEvent').fullCalendar('refetchEvents');
        alert('Agendamento realizado com sucesso!');
        $('#formAgendamento')[0].reset();
      },
      error: function(xhr) {
        $btn.removeClass('btn-progress disabled');
        let errorMsg = 'Erro ao agendar.';
        try {
          const errors = JSON.parse(xhr.responseJSON.errors);
          errorMsg = errors.data_inicio[0].message;
        } catch(e) {}
        alert(errorMsg);
      }
    });
  });
});
