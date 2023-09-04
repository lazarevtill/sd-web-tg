$.fn.lightboxify = function() {
	function i() {
		$(document.body).prepend(
			'<div class="lightbox-popup"><div class="lightbox-popup-dialog"><img class="lightbox-popup-image" /><p class="lightbox-popup-caption"></p></div></div>'
		);
	}
	function t(i, t, o) {
		var p = $('.lightbox-popup');
		p.find('.lightbox-popup-image').attr('src', i),
			p.find('.lightbox-popup-caption').html(t),
			o && 'function' == typeof o && o(p);
	}
	var o = this;
	i(),
		o.on('click', '.lightbox-item', function(i) {
			i.preventDefault();
			var o = $(this).attr('data-src'),
				p = $(this).attr('data-caption');
			t(o, p, function(i) {
				i.addClass('is-shown'),
					i.click(function() {
						i.removeClass('is-shown');
					});
			});
		});
};