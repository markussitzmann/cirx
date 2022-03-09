$('#upload-widget-warning-pane').hide();
$('#file-processing').hide();

$('#upload-file-clear-button').button().click(function(event) {
	event.preventDefault();
	$("#file_input_span").html('{{ file_form.file }}');
});

$('#create-file-clear-button').button().click(function(event) {
	event.preventDefault();
	$("textarea#id_string").val('');
});


$('#upload-widget-submit-button').button().click(function() {
	$('#upload-widget-warning-pane').hide();
	var fname = $('#upload-file-form #id_file').fieldValue()[0];
	var string = $('#upload-file-form #id_string').fieldValue()[0];
	if (fname==="" && string==="") {
		$('#upload-widget-warning-pane').text("Please specify a file either in 'Upload a File' or 'Create a File'").fadeIn();
		$('#id_file').parent().effect("highlight", {'color': '#FFD2D2'}, 10000);
		$('#id_string').effect("highlight", {'color': '#FFD2D2'}, 10000);
		return false;
	};
	if (fname!=="" && string!=="") {
		$('#upload-widget-warning-pane').text("Please clear one of both fields.").fadeIn();
		$('#id_file').parent().effect("highlight", {'color': '#FFD2D2'}, 10000);
		$('#id_string').effect("highlight", {'color': '#FFD2D2'}, 10000);
		return false;
	};

	$(this, "input[type='submit']").attr('disabled', 'true');
	$('.overlay :button').attr('disabled', 'true').css({'color': '#aaa', 'cursor': 'wait'});
	$('#upload-file-form').submit();
});
$('#upload-widget-close-button').button();

function updateProgressBar() {
	var dummy = Date();
	var url='{{ file_base_url }}/upload_progress?X-Progress-ID={{ upload_key }}'
	$.getJSON(url, {'dummy': dummy}, function(data, status) {
		if (null!=data.progress) {
			progress = Math.max(1, parseFloat(data.progress) * 100);
			clearTimeout(progressbar_timeout);
			setTimeout(updateProgressBar, 1000);
		} else {
			progress = 100;
			updateProcessingStatus();
			$('#file-processing').fadeIn();
			/*finished = 1;*/
		}
		$("#percentage").text(progress.toFixed(0) + '%');
		$("#progressbar").progressbar("option", "value", progress);
	});
}

function initProgressBar(arr, form, options) {
	$('#progressbar').progressbar({ value: 1});
	progressbar_timeout = setTimeout(updateProgressBar, 1000);
	return true;
};
$('#progressbar').progressbar({ value: 0.5 }).css({'background': '#eee'});

function updateProcessingStatus() {
	var dummy=Date();
	$.getJSON('{{ file_base_url }}/processing_status/{{ upload_key }}', {'dummy': dummy}, function(data, status) {
		$('#status-pane').html('<div><span>Reading structure record (max. 250): </span><strong>' + data.processed +'</strong></div>');
	});
	processing_timeout = setTimeout(updateProcessingStatus, 1000);
};

$('#upload-file-form')
	.ajaxForm({
		url: "{{ file_base_url }}/upload?X-Progress-ID={{ upload_key }}",
		beforeSubmit: initProgressBar,
		success: function(response, status, xhr, element) {
			clearTimeout(processing_timeout);
			window.location="{{ app_url }}"
		},
		error: function(response, status, xhr, element) {
			clearTimeout(processing_timeout);
			document.write(response);
		}
	})
	.append(
		$('<input />').attr('type', 'hidden').attr('name', 'upload_key').val('{{ upload_key }}')
	);
