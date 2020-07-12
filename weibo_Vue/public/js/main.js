
    $('#container').on('click','.bar6 form>button',function () {
        // $('#container .bar6 form>button').click(function () {
        var $key=$('#container .bar6 form input').val();
        var datas = {
            content:$key
        };
        console.log(datas);
        $.ajax({
            // url: 'http://192.168.31.158:5000/predict',
            url: 'http://127.0.0.1:5000/classify',
            type: 'post',
            dataType: 'json',
            data: datas,
            success: function (data) {
//                console.log(data);
//                var str='分类结果出错啦'
//                if(data.prediction=='2')
//                    str='这是一条正向的评论';
//                else if(data.prediction=='1')
//                    str='这是一条中肯的评论';
//                else if(data.prediction=='0')
//                    str='这是一条负向的评论';
                $('#result2').html(data.prediction);
            }
        });
    });
