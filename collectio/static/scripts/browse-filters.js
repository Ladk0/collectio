$(document).ready(function() {
    
    $('#filters').click(function(e) {
        e.stopPropagation();
    });
    
    function apply_filters() {
        filters = collect_filter_data()
        $.ajax({
            url: '',
            type: 'get',
            data: filters,
            success: function (data) {
                $('#cards_container').html(data);
            }
        });
    }

    function collect_filter_data() {
        var filters = {}

        $('.filter-input').each(function(i, obj) {
            var filter_val = $(this).val();
            var filter_key = $(this).data('filter');

            if (filter_key == 'sort_by') {
                if ($(obj).is(':checked')) {
                    filters[filter_key] = filter_val
                }
            } else if (filter_val && filter_val.length > 0) {
                filters[filter_key] = filter_val
            }
        })

        return filters
    }

    $('.filter-input').change(apply_filters);

    $('input[data-filter="sort_by"]').change(function() {
        if ($(this).is(':checked')) {
            if ($(this).val() == 'popularity') {
                $('#browse_title span').text('Popular ');
            } else if ($(this).val() == 'rating') {
                $('#browse_title span').text('Top rated ');
            }
        }
    })

    $('#reset_filters').click(function() {
        $('#sort_popularity').prop('checked', 'true');
        $('#browse_title span').text('Popular ');
        $('#status_filter_input').val('');
        $('#min_date_input').val('');
        $('#max_date_input').val('');
        $('#search_input').val('');
    });

    $('#sort_popularity').prop('checked', 'true').change();

    $('.search').on('input', function(){
        clearTimeout(this.delay);
        this.delay = setTimeout(function(){
           $(this).trigger('search');
        }.bind(this), 800);
    }).on('search', apply_filters);

    $('#cards_container').on('click', '#load_more button', function() {
        filters = collect_filter_data()
        filters['page'] = $(this).data('page');
        
        $.ajax({
            url: '',
            type: "get",
            data: filters,
            success: function (data) {
                var prepend = $('.card-container');
                $('#cards_container').html(data);
                $('.cards').prepend(prepend);
            }
        });
    });
});

