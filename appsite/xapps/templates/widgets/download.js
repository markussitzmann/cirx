$('#status-message').hide();

$('#download-widget-format-more-button').button({text: true, icons: {secondary: "ui-icon-triangle-1-e"}})
$('#download-format-button').buttonset();
$('#get3d-button').buttonset();


$('#download-widget-submit-button').button().click(function() {
	
	$('#status-message').fadeIn();	
	$(this, "input[type='submit']").attr('disabled', 'disabled');
	
	format = $('input:radio[name=download-format-choice]:checked').val();
	get3d = $('input:radio[name=get3d]:checked').val();
	download_url = '{{ file_base_url }}/{{ file.object.key.upload }}/download?format=' + format + '&get3d=' + get3d;
				
	var downloadURL = function(download_url) {
		var iframe;
		iframe = document.getElementById('hidden-downloader');
		if (iframe === null) {
			iframe = document.createElement('iframe');
			iframe.id = 'hidden-downloader'
			iframe.style.visibility = 'hidden';
			document.body.appendChild(iframe);
		}
		iframe.src = download_url;
		setTimeout(function(){ 
			$('#status-message').hide();
			$('#download-widget-submit-button').removeAttr('disabled');
			overlay_element.overlay().close()
		}, 5000);
		return false;
	}
	downloadURL(download_url);
});
$('#download-widget-close-button').button();