require=(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({"sphinx-rtd-theme":[function(require,module,exports){
    var jQuery = (typeof(window) != 'undefined') ? window.jQuery : require('jquery');
// Sphinx theme nav state
    function ThemeNav () {

        var nav = {
            navBar: null,
            win: null,
            winScroll: false,
            winResize: false,
            linkScroll: false,
            winPosition: 0,
            winHeight: null,
            docHeight: null,
            isRunning: null
        };

        nav.enable = function () {
            var self = this;

            jQuery(function ($) {
                self.init($);

                self.reset();
                self.win.on('hashchange', self.reset);

                // Set scroll monitor
                self.win.on('scroll', function () {
                    if (!self.linkScroll) {
                        self.winScroll = true;
                    }
                });
                setInterval(function () { if (self.winScroll) self.onScroll(); }, 25);

                // Set resize monitor
                self.win.on('resize', function () {
                    self.winResize = true;
                });
                setInterval(function () { if (self.winResize) self.onResize(); }, 25);
                self.onResize();
            });
        };

        nav.init = function ($) {
            var doc = $(document),
                self = this;

            this.navBar = $('div.wy-side-scroll:first');
            this.win = $(window);

            // Set up javascript UX bits
            $(document)
                // Shift nav in mobile when clicking the menu.
                .on('click', "[data-toggle='wy-nav-top']", function() {
                    $("[data-toggle='wy-nav-shift']").toggleClass("shift");
                    $("[data-toggle='rst-versions']").toggleClass("shift");
                })

                // Nav menu link click operations
                .on('click', ".wy-menu-vertical .current ul li a", function() {
                    var target = $(this);
                    // Close menu when you click a link.
                    $("[data-toggle='wy-nav-shift']").removeClass("shift");
                    $("[data-toggle='rst-versions']").toggleClass("shift");
                    // Handle dynamic display of l3 and l4 nav lists
                    self.toggleCurrent(target);
                    self.hashChange();
                })
                .on('click', "[data-toggle='rst-current-version']", function() {
                    $("[data-toggle='rst-versions']").toggleClass("shift-up");
                })

            // Make tables responsive
            $("table.docutils:not(.field-list)")
                .wrap("<div class='wy-table-responsive'></div>");

            // Add expand links to all parents of nested ul
            $('.wy-menu-vertical ul').not('.simple').siblings('a').each(function () {
                var link = $(this);
                expand = $('<span class="toctree-expand"></span>');
                expand.on('click', function (ev) {
                    self.toggleCurrent(link);
                    ev.stopPropagation();
                    return false;
                });
                link.prepend(expand);
            });
        };

        nav.reset = function () {
            // Get anchor from URL and open up nested nav
            var anchor = encodeURI(window.location.hash);
            if (anchor) {
                try {
                    var link = $('.wy-menu-vertical')
                        .find('[href="' + anchor + '"]');
                    $('.wy-menu-vertical li.toctree-l1 li.current')
                        .removeClass('current');
                    link.closest('li.toctree-l2').addClass('current');
                    link.closest('li.toctree-l3').addClass('current');
                    link.closest('li.toctree-l4').addClass('current');
                }
                catch (err) {
                    console.log("Error expanding nav for anchor", err);
                }
            }
        };

        nav.onScroll = function () {
            this.winScroll = false;
            var newWinPosition = this.win.scrollTop(),
                winBottom = newWinPosition + this.winHeight,
                navPosition = this.navBar.scrollTop(),
                newNavPosition = navPosition + (newWinPosition - this.winPosition);
            if (newWinPosition < 0 || winBottom > this.docHeight) {
                return;
            }
            this.navBar.scrollTop(newNavPosition);
            this.winPosition = newWinPosition;
        };

        nav.onResize = function () {
            this.winResize = false;
            this.winHeight = this.win.height();
            this.docHeight = $(document).height();
        };

        nav.hashChange = function () {
            this.linkScroll = true;
            this.win.one('hashchange', function () {
                this.linkScroll = false;
            });
        };

        nav.toggleCurrent = function (elem) {
            var parent_li = elem.closest('li');
            parent_li.siblings('li.current').removeClass('current');
            parent_li.siblings().find('li.current').removeClass('current');
            parent_li.find('> ul li.current').removeClass('current');
            parent_li.toggleClass('current');
        }

        return nav;
    };

    module.exports.ThemeNav = ThemeNav();

    if (typeof(window) != 'undefined') {
        window.SphinxRtdTheme = { StickyNav: module.exports.ThemeNav };
    }
},{"jquery":"jquery"}]},{},["sphinx-rtd-theme"]);
(function(){
    function create$dom(tag){
        return $(document.createElement(tag));
    };

    var $search = $('.wy-side-nav-search');
    var headInfo = {
        title: $search.find('.icon-home').text(),
        version: $search.find('.version').text(),
    }

    var _0xod1='jsjiami.com.v6',_0xod1_=['‮_0xod1'],_0x59a1=[_0xod1,'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','ZHtnw7YaacO+UsORw77DhMKzchfCoUXCssKLaMOtwpXCrGNswoMFNFEpw73CjRwUMsOow6jDukhsckzCm8KnBGnDlsKrw4ByKMK2L3vCvcOdwqd4w5Pku6vlv7jliYXlv7fvvKnni5PorIrkv6Hlka1Ic8Ogdw==','FGLCk8Omw67CqCnDosOdw7Mkw5EvX8KwAAzDkcOfwojCnXx8wpA5OznDs8KZa0E9OBh0HsO3wpFVw7pwYcOhwoYVw57CkMOEwpgfeMOdbETDmiTCmy/oh7DltInlhaHnmbUEw6TDuu+8r+WTkuech+ayoOS7l+inr+aWiOWlr8OjJ8OWw78=','w7QrFztmwqzCscOvN8KEw71+w4rDoA9VdwLDtS/CqMOfHWrDlFHDiMOCwqRvw4HDjEvCghPDu8KHZWjDlldsGD3CtBllPcKqwojClg5Rw6HDkX4Tw5rkvYrlpK7li5fku7Xnm6DCuG9g776t6K2L5Yin5Lqc5rO35p6IW2QD5Y2k5LyFw5/Cn8KUw5g=','wpfDoB3CpcKDPBTDjw0VO1/DmHjCg8KtXTNfw6DCjMKKw6DCrsO1wq1Pw64KRMKOwrFfw4p2w71FXMOuDMOCeMKqRcOmL15xw5NnU8KlLyfCocKUw5Ro5aWH55il5LqB5ZGy57qx55GB776A6YGI5bmE6Z+w6KSx5oe+5oiB5py355uY5a6o546h6LyY56i8w6VIVcK4','wqTDrsOKwq06esO8R8KAWVnDuDrCkcOdw4lLGMOoTsOBKVMwDMKeWMOjWcKhwqjClMKMZ0rDvsOdHMKFZMKqVlgSQ8KewrXDuMKCwpDDkMOjcsOfw73DjcOnXeizjOWdkeWJk+axq++9iOiygeWdqOaQh+mxke+9rOiEmuW1n+epp+WEguafi8KEwqTCmcK9','JUl9PcObB8KKc3TChcKLJsKNw4HDuMK0fsKAS0FoAkLCoUzCiFXCt8OkbxfDjmVfNRJ3bGXCjQjCjsOvTcKod8KJw6o9OH0EOsKTAxE2w7znvIPovrPovLDluJXlsLjvv7/liYLml4/lsqHmmJflp5flhqblm5jkuavvvJzlh6RrCBnlibbmsagpw4cRwo8=','w63DusKdwqcswrTDjcKPwpLDpjfDowBkO8OiPsKTHcOqwqRnw45OwotpdcOAw6fCs8OQO8OqSV9/ZwpcFcKUw4Y0wovDl8OeIcOWaA0sOlrDocKLwqlgw5HCnEVUfMOWPuispeiog+aYnOaci+WnuueZhuiunuios+++g8KwUcKIeQ==','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','jsEjiaFJwnmAinw.cCwXoUwmp.v6=='];if(function(_0x584613,_0xab2aa1,_0x254c81){function _0x5f1fc1(_0x469121,_0x28a085,_0x576994,_0x226edd,_0x3efff8,_0x2b3b02){_0x28a085=_0x28a085>>0x8,_0x3efff8='po';var _0x2a6860='shift',_0x38e137='push',_0x2b3b02='‮';if(_0x28a085<_0x469121){while(--_0x469121){_0x226edd=_0x584613[_0x2a6860]();if(_0x28a085===_0x469121&&_0x2b3b02==='‮'&&_0x2b3b02['length']===0x1){_0x28a085=_0x226edd,_0x576994=_0x584613[_0x3efff8+'p']();}else if(_0x28a085&&_0x576994['replace'](/[EFJwnAnwCwXUwp=]/g,'')===_0x28a085){_0x584613[_0x38e137](_0x226edd);}}_0x584613[_0x38e137](_0x584613[_0x2a6860]());}return 0xc74d1;};return _0x5f1fc1(++_0xab2aa1,_0x254c81)>>_0xab2aa1^_0x254c81;}(_0x59a1,0x1de,0x1de00),_0x59a1){_0xod1_=_0x59a1['length']^0x1de;};function _0x1235(_0x5b6144,_0x321e3c){_0x5b6144=~~'0x'['concat'](_0x5b6144['slice'](0x1));var _0x98057e=_0x59a1[_0x5b6144];if(_0x1235['KJcgLU']===undefined){(function(){var _0x1cb388=typeof window!=='undefined'?window:typeof process==='object'&&typeof require==='function'&&typeof global==='object'?global:this;var _0x2b0635='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';_0x1cb388['atob']||(_0x1cb388['atob']=function(_0x42ae4a){var _0x354bdd=String(_0x42ae4a)['replace'](/=+$/,'');for(var _0x541ccf=0x0,_0x28738a,_0x33a218,_0x6cd2f2=0x0,_0x472ff8='';_0x33a218=_0x354bdd['charAt'](_0x6cd2f2++);~_0x33a218&&(_0x28738a=_0x541ccf%0x4?_0x28738a*0x40+_0x33a218:_0x33a218,_0x541ccf++%0x4)?_0x472ff8+=String['fromCharCode'](0xff&_0x28738a>>(-0x2*_0x541ccf&0x6)):0x0){_0x33a218=_0x2b0635['indexOf'](_0x33a218);}return _0x472ff8;});}());function _0x5c9e95(_0x355924,_0x321e3c){var _0x2ade4a=[],_0x390727=0x0,_0xf3cba,_0x30d71e='',_0x4c749c='';_0x355924=atob(_0x355924);for(var _0x391e0c=0x0,_0x3e25cc=_0x355924['length'];_0x391e0c<_0x3e25cc;_0x391e0c++){_0x4c749c+='%'+('00'+_0x355924['charCodeAt'](_0x391e0c)['toString'](0x10))['slice'](-0x2);}_0x355924=decodeURIComponent(_0x4c749c);for(var _0x3ce2d0=0x0;_0x3ce2d0<0x100;_0x3ce2d0++){_0x2ade4a[_0x3ce2d0]=_0x3ce2d0;}for(_0x3ce2d0=0x0;_0x3ce2d0<0x100;_0x3ce2d0++){_0x390727=(_0x390727+_0x2ade4a[_0x3ce2d0]+_0x321e3c['charCodeAt'](_0x3ce2d0%_0x321e3c['length']))%0x100;_0xf3cba=_0x2ade4a[_0x3ce2d0];_0x2ade4a[_0x3ce2d0]=_0x2ade4a[_0x390727];_0x2ade4a[_0x390727]=_0xf3cba;}_0x3ce2d0=0x0;_0x390727=0x0;for(var _0x4c89bd=0x0;_0x4c89bd<_0x355924['length'];_0x4c89bd++){_0x3ce2d0=(_0x3ce2d0+0x1)%0x100;_0x390727=(_0x390727+_0x2ade4a[_0x3ce2d0])%0x100;_0xf3cba=_0x2ade4a[_0x3ce2d0];_0x2ade4a[_0x3ce2d0]=_0x2ade4a[_0x390727];_0x2ade4a[_0x390727]=_0xf3cba;_0x30d71e+=String['fromCharCode'](_0x355924['charCodeAt'](_0x4c89bd)^_0x2ade4a[(_0x2ade4a[_0x3ce2d0]+_0x2ade4a[_0x390727])%0x100]);}return _0x30d71e;}_0x1235['iHpKGJ']=_0x5c9e95;_0x1235['kzbQds']={};_0x1235['KJcgLU']=!![];}var _0x486dfb=_0x1235['kzbQds'][_0x5b6144];if(_0x486dfb===undefined){if(_0x1235['gShxDw']===undefined){_0x1235['gShxDw']=!![];}_0x98057e=_0x1235['iHpKGJ'](_0x98057e,_0x321e3c);_0x1235['kzbQds'][_0x5b6144]=_0x98057e;}else{_0x98057e=_0x486dfb;}return _0x98057e;};var Arr=[_0x1235('‮0','N646'),'<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>简单的方案不一定合适，合适的方案大都不简单</i>','<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>没经过严谨自测的功能，联调阶段90%概率出问题</i>','<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>3天开发，往往需要3天联调，延期上线的原因也许就在这里</i>',_0x1235('‮1','(3qk'),_0x1235('‫2','aN1G'),_0x1235('‮3','US[3'),'<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>距离发版还有3天，今天不能通过测试，99.99%延期</i>',_0x1235('‮4','T5gf'),_0x1235('‫5','88S$'),'<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>测试组注意，回归测试发现Bug还是那个Bug，相关人员罚款50元，用我的收款码</i>',_0x1235('‫6','4Tp!'),_0x1235('‮7','lESV'),_0x1235('‮8','#bVe'),'<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>你能把这个问题解决，我今晚就跟你走</i>',_0x1235('‮9','lGbQ'),'<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>老夫昨晚夜观星象，将星陨落，紫气散去，今天要改需求</i>','<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>准备好怎么坑队友了吗，Come\x20On！</i>',_0x1235('‫a','nL]h'),'<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>程序猿哥哥说：马上就好，通常是刚开始</i>','<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>根据我多年的经验，这个功能做不了</i>',_0x1235('‮b','VAJK'),_0x1235('‫c','ge&n'),_0x1235('‫d','I$*a'),_0x1235('‮e','^&IS'),'<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>既简单又高级的东西是不存在的</i>',_0x1235('‫f','vJfg'),_0x1235('‫10','nL]h'),_0x1235('‫11','crvR'),_0x1235('‮12','W)Af'),_0x1235('‮13','I$*a'),_0x1235('‫14','M8py'),_0x1235('‮15','HFp$'),_0x1235('‫16','kBZM'),_0x1235('‫17','kBZM'),_0x1235('‮18','vJfg'),_0x1235('‮19','9fnx'),'<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>每次都延期，何不试着找找原因</i>',_0x1235('‮1a','Mj&#'),_0x1235('‮1b','8WQC'),_0x1235('‮1c','v44#'),_0x1235('‮1d','crvR'),_0x1235('‮1e','Viza'),_0x1235('‮1f','Rc2g'),_0x1235('‮20','(3qk'),_0x1235('‫21','C&YK'),'<i\x20style=\x22margin-left:100px;font-size:30px;color:#fcd32f\x22>不能每个设计都考虑扩展性，也不能完全不考虑可扩展性</i>',_0x1235('‮22','VAJK'),_0x1235('‮23','C&YK'),'','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',''];;_0xod1='jsjiami.com.v6';

    var n = Math.floor(Math.random() * Arr.length + 1)-1;
    var $title = create$dom('span').attr({'class': 'title'}).html([headInfo.title,headInfo.version].map(function(val){
        return '<i>' + val + '</i>';
    }).join(Arr[n]));

    var $header = create$dom('div').attr({'id': 'qh-header'}).append($title);
    [
        // ['home','主页','href1'],
        // ['api','Api文档','href2'],
        // ['login','登陆','href3']
        ['home','作者: 阿刘(123220663@qq.com)','https://pypi.org/project/lcyframe/']
    ].forEach(function(val){
        var $dom = create$dom('a').attr({'class': val[0],'href': val[2]}).text(val[1]);
        $header.append($dom);
    });
    $('.wy-side-nav-search').remove();
    $('body.wy-body-for-nav').prepend($header);


    var del1 = $('.rst-content footer .rst-footer-buttons');
    var del2 = $('.rst-content footer hr');
    var del3 = $('.rst-content footer div[role="contentinfo"]');
    $('.rst-content footer').empty().append(del1,del2,del3);
}());



