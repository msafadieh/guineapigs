$(document).ready(function() {
	function sendForm(url) {
		return function(event) {
			event.preventDefault();
			$.post(url, data=$('#modal-form').serialize(), function(data) {
				if (data.status == 'ok') {
					$('#modal').modal('hide');
					location.reload();
				}
				else {
					$('#modal-content').html(data);
					$('#submit-btn').click(sendForm(url));
				}
			});
		}
	}

	$(".modal-btn").each((_, v) => {
		const url = v.parentElement.action;
		v.onclick = e => {
			e.preventDefault();
			$.get(url, data => {
				$('#modal-content').html(data);
				$('#modal').modal();
				$('#submit-btn').click(sendForm(url));
			});
		}
	});
});