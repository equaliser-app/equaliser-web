$(document).ready(function(){
	$('.carousel').slick({
		slidesToShow: 4,
		slidesToScroll: 1,
		adaptiveHeight: true,
		variableWidth: true
	});
	
	$('*[data-bg]').each(function() {
		var imageUrl = $(this).attr('data-bg');
		$(this).css('background-image', 'url(' + imageUrl + ')');
	});

	$('#get-ephemeral-token').click(function(e) {
	    e.preventDefault();
	    $(this).replaceWith('<img alt="Token" src="/ephemeral-token">');
	    $("html, body").animate({ scrollTop: $(document).height() }, "slow");
	});
});