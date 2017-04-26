var API_BACKEND = 'http://192.168.0.20:8080'

if (user_info != null) {
    var attendees = [user_info['username']];
}

function format_seconds(secs) {
    secs = Math.floor(secs);
    var minutes = Math.floor(secs / 60);
    var seconds = secs - (minutes * 60);

    var minutes_unit = minutes == 1 ? 'minute' : 'minutes';
    var seconds_unit = seconds == 1 ? 'second' : 'seconds';

    if (minutes < 0) {
        minutes = 0;
        seconds = 0;
    }

    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    if (seconds < 10) {
        seconds = "0" + seconds;
    }
    return minutes + ' <span>' + minutes_unit + '</span> &nbsp; ' + seconds +
            ' <span>' + seconds_unit + '</span>';
}

function create_attendee(info) {
    var str = '<li><div class="row"><div class="col-sm-6"><p>' +
        info['forename'] + ' ' + info['surname'] + ' <span>' + info['username'] + '</span></p>' +
        '</div><div class="col-sm-6">';
    if (info['username'] != user_info['username']) {
        str += '<a class="btn warning gift-attendee">Gift</a>';
    }
    str += '<a class="btn red delete-attendee">Delete</a></div></div></li>';
    return $(str);
}

function add_attendee() {
    var username = $('#add-member-field').val();
    $('#add-member-field').val('');
    $.ajax({
        dataType: 'json',
        url: API_BACKEND + '/usernames',
        data: {'query': username},
        success: function(data, textStatus, jqXHR) {
            console.log(attendees);
            users = data['result']
            if (users.length == 0) return;
            if (attendees.indexOf(users[0]['username']) >= 0) return;
            attendees.push(users[0]['username']);
            var $elem = create_attendee(users[0]);
            $('.attendee-list').append($elem);
            $('#attendee-count').text(parseInt($('#attendee-count').text()) + 1);
        }
    });
}

function updateCountdowns() {
    var now = Date.now() / 1000;
    $('.countdown').each(function() {
        var deadline = parseFloat($(this).attr('data-deadline'));
        //console.log("deadline: " + deadline);
        //console.log("now: " + now);
        var left = deadline - now;
        //console.log(left);
        $(this).html(format_seconds(left));
    });
}

function inject_attendee_list() {
    $('.attendee-list').children().each(function() {
        var username = $(this).find('span').text();
        $('<input>').attr({
            type: 'hidden',
            name: 'attendees[]',
            value: username
        }).appendTo('form');

        var isGuest = $(this).find('.gift-attendee').hasClass('checked');
        if (isGuest) {
            $('<input>').attr({
                type: 'hidden',
                name: 'guests[]',
                value: username
            }).appendTo('form');
        }
    });
}

function inject_tier_list() {
    var rank = 1;
    $('.tier-list').children().each(function() {
        var tierId = $(this).find('.row').attr('data-tier-id');
        if ($(this).find('.btn').hasClass('checked')) {
            console.log('Tier ' + tierId + ' is checked');
            $('<input>').attr({
                type: 'hidden',
                name: tierId,
                value: rank++
            }).appendTo('form');
        }
    });
}


$(document).ready(function() {
    updateCountdowns();
    setInterval(updateCountdowns, 1000);

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

    $('#add-member-field').autocomplete({
        minLength: 2,
        source: function(request, response) {
            var query = request.term;
            $.ajax({
                dataType: 'json',
                url: API_BACKEND + '/usernames',
                data: {'query': query},
                success: function(data, textStatus, jqXHR) {
                    users = data['result'].map(function(elem) {
                        return {
                            'label': elem['forename'] + ' ' + elem['surname'] +
                                ' (' + elem['username'] + ')',
                            'value': elem['username']
                        }
                    })
                    response(users)
                }
            });
        }
    });

    $('#add-member').click(add_attendee);
    $('#add-member-field').on("keypress", function(e) {
        if (e.which != 13) return;
        e.preventDefault();
        add_attendee();
    });

    $('.attendee-list').on("click", '.delete-attendee', function(e) {
        e.preventDefault();
        $(this).closest('li').remove();
        $('#attendee-count').text(parseInt($('#attendee-count').text()) - 1);
        if ($(this).prev().hasClass('checked')) {
            $('#gift-count').text(parseInt($('#gift-count').text()) - 1);
        }
        var username = $(this).parent().parent().children().first().find('p').find('span').text();
        var index = attendees.indexOf(username);
        attendees.splice(index, 1);
    });

    $('.attendee-list').on("click", '.gift-attendee', function(e) {
        e.preventDefault();
        if ($(this).hasClass('checked')) {
            $(this).text('Gift');
            $('#gift-count').text(parseInt($('#gift-count').text()) - 1);
        }
        else {
            $(this).text('Gifted');
            $('#gift-count').text(parseInt($('#gift-count').text()) + 1);
        }
        $(this).toggleClass('checked');
    });

    $('.tier-list').sortable();
    $('.tier-list').disableSelection();

    $('.tier-list').on("click", '.btn.success', function(e) {
        e.preventDefault();
        var current_count = parseInt($('#tier-count').text(), 10);
        if ($(this).hasClass('checked')) {
            if (current_count == 1) {
                alert('At least one tier must be selected');
                return;
            }
            $(this).text('Join').removeClass('checked');
            $('#tier-count').text(current_count - 1);
        }
        else {
            $(this).text('Leave').addClass('checked');
            $('#tier-count').text(current_count + 1);
        }
    });

    $('#attendees-submit').click(function(e) {
        e.preventDefault();
        inject_attendee_list();
        $('form').submit();
    });

    $('#tiers-submit').click(function(e) {
        e.preventDefault();
        inject_tier_list();
        $('form').submit();
    });
});
