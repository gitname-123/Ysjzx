
const { JSDOM } = require("jsdom");
const dom = new JSDOM(`<!DOCTYPE html><html><body></body></html>`);
window = dom.window;
document = window.document;
XMLHttpRequest = window.XMLHttpRequest;

delete __filename;
delete __dirname;
function get_enviroment(proxy_array) {
    for (var i = 0; i < proxy_array.length; i++) {
        handler = '{\n' +
            '    get: function(target, property, receiver) {\n' +
            '        console.log("方法:", "get  ", "对象:", ' +
            '"' + proxy_array[i] + '" ,' +
            '"  属性:", property, ' +
            '"  属性类型:", ' + 'typeof property, ' +
            // '"  属性值:", ' + 'target[property], ' +
            '"  属性值类型:", typeof target[property]);\n' +
            '        return target[property];\n' +
            '    },\n' +
            '    set: function(target, property, value, receiver) {\n' +
            '        console.log("方法:", "set  ", "对象:", ' +
            '"' + proxy_array[i] + '" ,' +
            '"  属性:", property, ' +
            '"  属性类型:", ' + 'typeof property, ' +
            // '"  属性值:", ' + 'target[property], ' +
            '"  属性值类型:", typeof target[property]);\n' +
            '        return Reflect.set(...arguments);\n' +
            '    }\n' +
            '}'
        eval('try{\n' + proxy_array[i] + ';\n'
            + proxy_array[i] + '=new Proxy(' + proxy_array[i] + ', ' + handler + ')}catch (e) {\n' + proxy_array[i] + '={};\n'
            + proxy_array[i] + '=new Proxy(' + proxy_array[i] + ', ' + handler + ')}')
    }
}

function watch(obj, name) {
    return new Proxy(obj, {
        get: function (target, property, receiver) {
            try {
                if (typeof target[property] === "function") {
                    console.log("对象 => " + name + ",读取属性:" + property + ",值为:" + 'function' + ",类型为:" + (typeof target[property]))
                } else {
                    console.log("对象 => " + name + ",读取属性:" + property + ",值为:" + target[property] + ",类型为:" + (typeof target[property]))
                }
            } catch (e) {
            }
            return target[property]
        },
        set: (target, property, newValue, receiver) => {
            try {
                console.log("对象 => " + name + ",设置属性:" + property + ",值为:" + newValue + ",类型为:" + (typeof newValue))
            } catch (e) {
            }
            return Reflect.set(target, property, newValue, receiver)
        }
    })
}
proxy_array = ['window', 'document', 'location', 'navigator', 'history', 'screen',"Object"]

var content="{qqhOXsM2ludZMTqY2ntYuS6k7n6zgNQOeF9YKqhLeCDkPyZiPUqr0qk130qt1083179040ql4096qhWBlAqdwK_XZqr4qr0qr0qr7qr0qVpmpT36rvQDYnRoRjQCyaq.kDHK4sj0MQTPWYoG6s2SZBlkxZ6g.KZjHUaiDt5xOd3qqqqqc64qc64qlFHeo!x7z,aac,amr,asm,avi,bak,bat,bmp,bin,c,cab,css,csv,com,cpp,dat,dll,doc,dot,docx,exe,eot,fla,flc,fon,fot,font,gdb,gif,gz,gho,hlp,hpp,htc,ico,ini,inf,ins,iso,js,jar,jpg,jpeg,json,java,lib,log,mid,mp4,mpa,m4a,mp3,mpg,mkv,mod,mov,mim,mpp,msi,mpeg,obj,ocx,ogg,olb,ole,otf,py,pyc,pas,pgm,ppm,pps,ppt,pdf,pptx,png,pic,pli,psd,qif,qtx,ra,rm,ram,rmvb,reg,res,rtf,rar,so,sbl,sfx,swa,swf,svg,sys,tar,taz,tif,tiff,torrent,txt,ttf,vsd,vss,vsw,vxd,woff,woff2,wmv,wma,wav,wps,xbm,xpm,xls,xlsx,xsl,xml,z,zip,apk,plist,ipaHooQzpnTrhll.AP7|vt.ZKT91aU4Vtz2iusd9E.ViPsjxl_GjGsBQE2oKOptmm.0_AwIEtB0Xds5gEf9nfMRpe79DcUMRQPmPOREAFOKv7DyJ9NmbXQLeu.U4K8FgI26PU8Lq3CvjTpjrXG0X6AhLRNUccQhTwbUjkI4r7.pni8QpvjbbJ3Mp8.lCaRhSc.CDZKupQVmJ0rVfzYTNNsmyu1rT33U9mQ0RDF2ew1SybUvwpVaYbDmRkYKgCcCJt82ynmONMQSN3U12G8KwLIKS2QDm1MrJ_3Yf1cpL816m9rPlmRq7PDOSFWalSkCVhEa0bmGqqqkm4Zqr0qr1q.JNY8gVhbkte2n95.Y_EHaUv7s_0lyvvBDJN7bV83kNWqDfcb0f2qQsVS4wU24I6NTwvybwKR5R6ebICr0q!TKSEqFU92F1lRMaTcJoL0ArJS3Tl3ssE7WmWQHDmlJYV6sUwWh9Z6ckYAJ0N611ylJaVTUuwow0EXAswuwa0RQOrfJalkpn0qM93BQbSS36qcVkyh8AlqVPypJSET1OQ7wnZXhOwBJsl6tUQLhP76RkVZJn3DR69ihGVFqS9yicW_RpfZFqqgHpQOouQFwKlkJ1a6JvQThOq6QsV.JuJ6kPgJJ0gTmOQEwa7XcOQ_w0LthqWWmmaKJK0eHnQQtc0OqurODOG08VgqDngFJT7TksQYwSAXmuwAJAG6lvQphXa6.sU6J5ZDjovzthZs_kIBlZgUSDB2czW_ykdpDHG_7botJ8Q6d6I_hB96XOUPJdp6en4CJ4QT_sISwdqXZuIewgWn4OiKWQaL4AHaM7WR6CCFJ8AO4K6.8RQqac4kJyaTSkI8we0XCk8RJQW6C6IKhzV62OUiJeqD9UvJlQNz7fCBHjqRzub.DMqIfpCxDxlQ_CDpJMg6Lo8OhjE6guK2J4T6Bc_dJdGTLk8_w49Xzk8lxB3T.O8arzQq~RHxw6NTBqYWyM.qIzUd0WZAvQK_piZUoNK7rSCGIERHxxgm4CMxWJnbs8KexaeGIFrxTxybu3wgNBSv6V8WqEOAI4M50E6KdUMEmNO9Ub1LyBdaIHQIfRP2tlkBfIfCFbVyrnBaId1jRzGKuncFNljmb5YRfX_aBNUMeKgmcfKySxb6K0YEqojbjT8RwsB0j2FL9WymbkKhpnLDnvs3ee2a8VQMy9X0C4s4yyPqBUkj2bNbnwY3YMBvj9lNYI2GnskNA1vVdkMQLlv9UJVLYeNl5ylN283GTvkCqsFVgdk6rlw0znYmSyK9eDr2fR1Ae81TGEioQvMPNBEvJ8wvZh3mx7Q2Aqq";
// var content="jCfMQcmM1Cab6ZuI1YEnuG6.cMDP9MUCLEc4vKShu6rz98Shwsya8ufNxGeS1br3";
window=global;
window.top=window;
window.self=window;
//补的一些环境
//window环境
function Window() {}
// window.Window = Window;


// window.name='$_YWTU=NQhlym4_83RxhkaVshEtJHR6zTL9L_1TvNok567zDIA&$_YVTX=iq&vdFm='
window.addEventListener=function (){
    console.log("window的addEventListener",arguments)
};
window.attachEvent=function (){
    console.log("window的attachEvent",arguments)
};
// window.chrome={
//     "app": {
//         "isInstalled": false,
//         "InstallState": {
//             "DISABLED": "disabled",
//             "INSTALLED": "installed",
//             "NOT_INSTALLED": "not_installed"
//         },
//         "RunningState": {
//             "CANNOT_RUN": "cannot_run",
//             "READY_TO_RUN": "ready_to_run",
//             "RUNNING": "running"
//         }
//     }
// }
window.ActiveXObject=function(arg){
    console.log("window的ActiveXObject=====>",arg)
};
// window.Request=function(arg){
//     console.log("window的Request=====>",arg)
// };
// window.fetch=function(arg){
//     console.log("window的fetch=====>",arg)
// }
window.XMLHttpRequest=require("xmlhttprequest").XMLHttpRequest;
// window.indexedDB={};
// window.DOMParser=function(arg){
//     console.log("window的DOMParser=====>",arg)
// }

localStorage={
    "_$rc": "y6qL8vePUXK888QReYwUbagneJDRxtDuBDDbgkTBMdHfyaVsLuxYhW.zuQ2NbyFwlWuAnXAl1LzNII2ffdZt3D21lOhdFeIhcmCfAiFa9_aIOOwf004HvGHIw5V8lShYBSG3jBClo.dE5IDGXunIRm.GKd5JmNssLsecc8qkGjcpIFGutnacFcSUOu0OV42vUxmmgjrevMqdMD6F.LeujtMmPderLJV_7l9_xWgtUOpurMCxMsp_iPzdCsB4M3yfUtvjzctFg4vHhxFD8ciH6XJY.9JH1jRG6TWVg.RLKwP5n0mf6MWxp8zeQ4fdrhMtksJMP6m_uu0KvHzGA6A1il2eZE_4dQt9UodxZ4MbnnrmWBEX67vX2bc6VrcPzWXvQ075l5Rm0fsKd55YU6BMFwVIpUHS.tq2Di3OxA3Xa99MS1BJBysaek.bsSE.gJrEgwQknbLoECznbjiCyuVyg3Z9rTiGy4NKlZGGxy0bVQoYP2Wa2cQFiuD6R2fEQD_FxyCxWvRgnkpk_E2hDZuJlcYBfUa3QRvcz_09fFP5dM_T4y_p5yK4HWtKLn_u14cTp7BcO77QUXmqGKU_DcTScW1Ckfo4GP4AthMUIwVt_UuwRV8akm1qe_w.UNAceVCgNwbnwBHLy4mIeDhtQafYeiKgc8WGjDvliIAucrgkes_ZwvGYuEJyaIMQPP4wwqSmBSDHSZWIRdxoeTxl2UMfQ9NW5uaceIqWL5_V9uyecBNG6T3x1SBpQFm86JOiS0RVrKcPacbQn_cUQ6kw",
    "gr_imp_1010771310": "{\"expiredAt\":1742436676984,\"value\":false}",
    "TY_DISTINCT_ID": "7542867d-b5a9-457b-aeb6-c4468c21c86e",
    "footer_1741257013505": "{\"value\":{\"info\":\"<script id=\\\"footer_temp\\\" type=\\\"text/html\\\">\\r\\n\\t <div class=\\\"footer\\\" style=\\\"clear:both;\\\">\\r\\n            <div class=\\\"footer_one \\\">\\r\\n                <div class=\\\"wrap1200 clear\\\">\\r\\n                    <div class=\\\"service_center disib clear fl\\\">\\r\\n                        <dl>\\r\\n                            <dt>\\r\\n                                <a href=\\\"/noauth/helpcenter/index\\\" target=\\\"_blank\\\" class=\\\"link_color\\\">帮助中心</a>\\r\\n                            </dt>\\r\\n                            <dd>\\r\\n                                <a href=\\\"http://robot.ouyeel.com/robot/ouyeel.html?sysNum=1488163057722509\\\" target=\\\"_blank\\\" class=\\\"mt15\\\" style=\\\"\\\">在线客服</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"/noauth/helpcenter/helpfile#maodian_200101\\\" target=\\\"_blank\\\" class=\\\"mt10\\\" style=\\\"\\\">买家指南</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"/noauth/helpcenter/helpfile#maodian_200201\\\" target=\\\"_blank\\\" class=\\\"mt10\\\" style=\\\"\\\">卖家指南</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"/home-ng/rule/-2\\\" target=\\\"_blank\\\" class=\\\"mt10\\\" style=\\\"\\\">发票说明</a>\\r\\n                            </dd>\\r\\n                        </dl>\\r\\n                        <dl>\\r\\n                            <dt>平台规则</dt>\\r\\n                            <dd>\\r\\n                                <a href=\\\"/home-ng/rule/2\\\" target=\\\"_blank\\\" class=\\\"mt15\\\">服务协议</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"/home-ng/rule/8\\\" target=\\\"_blank\\\" class=\\\"mt10\\\">交易规则</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"/home-ng/rule/4\\\" target=\\\"_blank\\\" class=\\\"mt10\\\">隐私条款</a>\\r\\n                            </dd>\\r\\n                        </dl>\\r\\n                        <dl>\\r\\n                            <dt>合同模板</dt>\\r\\n                            <dd>\\r\\n                                <a href=\\\"{{staticsPath}}/S3?fileName=现货交易合同(全额_分期付款)_买家.xls&path=public_HeTongMoBan/现货交易合同(全额_分期付款)_买家.xls\\\" target=\\\"_blank\\\" class=\\\"mt15\\\">采购合同（现货）</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"{{staticsPath}}/S3?fileName=现货交易合同(全额_分期付款)_卖家.xls&path=public_HeTongMoBan/现货交易合同(全额_分期付款)_卖家.xls\\\" target=\\\"_blank\\\" class=\\\"mt10\\\">销售合同（现货）</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"{{staticsPath}}/S3?fileName=产能预售交易合同_买家.zip&path=public_HeTongMoBan/产能预售交易合同_买家.zip\\\" target=\\\"_blank\\\" class=\\\"mt10\\\">采购合同（产能预售）</a>\\r\\n                            </dd>\\r\\n                        </dl>\\r\\n                        <dl>\\r\\n                            <dt>支付方式</dt>\\r\\n                            <dd>\\r\\n                                <a href=\\\"/home-ng/rule/-3\\\" target=\\\"_blank\\\" class=\\\"mt15\\\">在线支付</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"/home-ng/rule/-5\\\" target=\\\"_blank\\\" class=\\\"mt10\\\">余额支付</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"/home-ng/rule/-4\\\" target=\\\"_blank\\\" class=\\\"mt10\\\">银行承兑汇票</a>\\r\\n                            </dd>\\r\\n                        </dl>\\r\\n                        <dl>\\r\\n                            <dt>\\r\\n                                <a href=\\\"http://www.ouyeel.cn/\\\" target=\\\"_blank\\\" class=\\\"link_color\\\">关于欧冶</a>\\r\\n                            </dt>\\r\\n                            <dd>\\r\\n                                <a href=\\\"http://www.ouyeel.cn/about/profile\\\" target=\\\"_blank\\\" class=\\\"mt15\\\">欧冶简介</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"http://www.ouyeel.cn/recruitment/talent_concept\\\" target=\\\"_blank\\\" class=\\\"mt10\\\">欧冶招聘</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"https://www.ouyeel.cn/1018\\\" target=\\\"_blank\\\" class=\\\"mt10\\\">2023钢铁产业互联网交易节官网</a>\\r\\n                            </dd>\\r\\n                            <dd>\\r\\n                                <a href=\\\"http://www.ouyeel.cn/contact/marketing_network\\\" target=\\\"_blank\\\" class=\\\"mt10\\\">联系我们</a>\\r\\n                            </dd>\\r\\n                        </dl>\\r\\n                    </div>\\r\\n                    <div class=\\\"disib ou_steel_app fl\\\">\\r\\n                        <span class=\\\"app_txt\\\">欧冶钢好APP</span>\\r\\n                        <span class=\\\"app_img mt10 disib\\\">\\r\\n                              <img src=\\\"{{staticsPath}}/home/assets/images/Ewm.jpg\\\">\\r\\n                        </span>\\r\\n                    </div>\\r\\n                </div>\\r\\n            </div>\\r\\n            <div class=\\\"footer_two\\\" style=\\\"height: auto;\\\">\\r\\n                <div class=\\\"wrap1200 pr clear footer_two_pd font12\\\">\\r\\n                    <div class=\\\"link_address  txtL\\\">\\r\\n                        <a href=\\\"http://www.ouyeel.cn/\\\" target=\\\"_blank\\\" style=\\\"padding-left: 0\\\">欧冶云商门户</a>\\r\\n                        <a href=\\\"http://www.shgt.com/\\\" target=\\\"_blank\\\" target=\\\"_blank\\\">上海钢铁交易中心</a>\\r\\n                        <a href=\\\"/sls-ng\\\" target=\\\"_blank\\\">欧冶物流</a>\\r\\n                        <a href=\\\"https://www.ouyeelintl.com/\\\" target=\\\"_blank\\\">欧冶国际</a>\\r\\n                        <a href=\\\"https://www.ouyeel.com/open-capacity\\\" target=\\\"_blank\\\">能力开放</a>\\r\\n                        <a id=\\\"to_BSOL\\\"  href=\\\"javascript:void(0)\\\" >循环宝</a>\\r\\n                        <a href=\\\"/noauth/page/index_new/ouYeAppIndex\\\" target=\\\"_blank\\\" target=\\\"_blank\\\">欧冶钢好APP</a>\\r\\n                        <a href=\\\"http://www.steelhome.cn/\\\" target=\\\"_blank\\\" target=\\\"_blank\\\">钢之家</a>\\r\\n                    </div>\\r\\n                    <div class=\\\"mt10 txtL color_999 lh16 \\\">\\r\\n                        欧冶云商地址：中国上海宝山区漠河路600号A座28F 邮编：201999\\r\\n                    </div>\\r\\n                    <div class=\\\"mt10 txtL color_999 lh16 \\\">\\r\\n                        <span class=\\\"disib pr10 add_line\\\">版权所有2016 欧冶云商股份有限公司 <a href=\\\"https://beian.miit.gov.cn/#/Integrated/index\\\" class=\\\"c_999\\\">沪ICP备15018773号-1</a></span>\\r\\n                        <span class=\\\"disib pl10 add_line\\\"><a href=\\\"http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=31011302006234\\\" class=\\\"c_999\\\"><img src=\\\"{{staticsPath}}/public2/images/beian.png\\\" height=\\\"16\\\" width=\\\"16\\\" class=\\\"vb\\\">沪公网安备 31011302006234 号 </a></span>\\r\\n                    </div>\\r\\n\\r\\n                    <div class=\\\"pa_img\\\">\\r\\n                        <a href=\\\"http://www.itrust.org.cn/Home/Index/itrust_certifi/wm/PJ2019092501.html\\\" target=\\\"_blank\\\">\\r\\n                            <img src=\\\"{{staticsPath}}/home/assets/images/btm_img005.jpg\\\" class=\\\"mr10\\\" width=\\\"113\\\" height=\\\"36\\\">\\r\\n\\r\\n                        </a>\\r\\n                        <a href=\\\"http://wap.scjgj.sh.gov.cn/businessCheck/verifKey.do?showType=extShow&serial=9031000020190809152720000004925577-SAIC_SHOW_310000-20160407103236746104&signData=MEUCIBx7oxkz7rOE+VSqUV6VjLLYpjE3PgiDw3h1naHrdZg/AiEA55Tw6HNCyUmP7vYkSoJfTif07Q5gTx53CcKMvJBZWKg=\\\" target=\\\"_blank\\\">\\r\\n                            <img src=\\\"{{staticsPath}}/home/assets/images/btm_img002.jpg\\\" class=\\\"mr10\\\"  width=\\\"36\\\" height=\\\"36\\\">\\r\\n                        </a>\\r\\n                        <a href=\\\"http://www.cyberpolice.cn/wfjb/\\\" target=\\\"_blank\\\">\\r\\n                            <img src=\\\"{{staticsPath}}/home/assets/images/btm_img003.jpg\\\" width=\\\"93\\\" height=\\\"36\\\">\\r\\n                        </a>\\r\\n                    </div>\\r\\n                </div>\\r\\n            </div>\\r\\n\\r\\n            <div class=\\\"footer_three\\\">\\r\\n                <div class=\\\"wrap1200 clear footer_three_pd bg_color_f4 font12\\\">\\r\\n                    <div class=\\\"disib color_999 lh22 fl w65\\\">友情链接：</div>\\r\\n                    <div class=\\\"disib fl nr_show\\\">\\r\\n                        <!--友情链接-->\\r\\n                        <div class=\\\"lh22\\\">\\r\\n                            <a href=\\\"http://www.baowugroup.com/#/\\\" target=\\\"_blank\\\">中国宝武</a>\\r\\n                            <a href=\\\"https://www.baosteel.com/home\\\" target=\\\"_blank\\\">宝钢股份</a>\\r\\n                            <a href=\\\"https://www.sinosteel.com/\\\" target=\\\"_blank\\\">中钢集团</a>\\r\\n                            <a href=\\\"https://www.magang.com.cn/\\\" target=\\\"_blank\\\">马钢集团</a>\\r\\n                            <a href=\\\"http://www.tisco.com.cn/\\\" target=\\\"_blank\\\">太钢集团</a>\\r\\n                            <a href=\\\"http://www.bygt.com.cn/\\\" target=\\\"_blank\\\">八一钢铁</a>\\r\\n                            <a href=\\\"http://www.bxsteel.com/\\\" target=\\\"_blank\\\">本钢集团 </a>\\r\\n                            <a href=\\\"https://www.shougang.com.cn/sgweb/html/index.html\\\" target=\\\"_blank\\\">首钢集团 </a>\\r\\n                            <a href=\\\"http://www.sha-steel.com/\\\" target=\\\"_blank\\\">沙钢集团</a>\\r\\n                            <a href=\\\"http://www.ejianlong.com/d/jl001/homepage.jsp\\\" target=\\\"_blank\\\">建龙集团 </a>\\r\\n                            <a href=\\\"http://gxslyj.com/\\\" target=\\\"_blank\\\">盛隆冶金</a>\\r\\n                        </div>\\r\\n                        <!--央企电商另起一行-->\\r\\n                        <div class=\\\"lh22\\\">\\r\\n                            <a href=\\\"https://www.yzw.cn/\\\" target=\\\"_blank\\\">云筑网</a>\\r\\n                            <a href=\\\"http://www.crecgec.com/portal.php\\\" target=\\\"_blank\\\">鲁班网</a>\\r\\n                            <a href=\\\"https://www.zgdzwz.com/index.php?view=index&needCache=1\\\" target=\\\"_blank\\\">大宗物资网</a>\\r\\n                            <a href=\\\"http://ec.ceec.net.cn/\\\" target=\\\"_blank\\\">能建电商</a>\\r\\n                            <a href=\\\"http://www.hkrsoft.com/\\\" target=\\\"_blank\\\">华科软</a>\\r\\n                            <a href=\\\"https://www.cncecyc.com/store/index\\\" target=\\\"_blank\\\">化学云采</a>\\r\\n                        </div>\\r\\n                    </div>\\r\\n                </div>\\r\\n            </div>\\r\\n        </div>\\r\\n</script>\"},\"time\":1742350277655,\"expire\":86400000}",
    "slider_1741257013505": "{\"value\":{\"info\":\"<div class=\\\"global_sidebar common_slider normal_screen\\\">\\r\\n    <ul>\\r\\n        <li class=\\\"headset\\\">\\r\\n            <a href=\\\"javascript:;\\\" class=\\\"m_robot_btn\\\">\\r\\n                <i class=\\\"icon iconfont icon-zaixianxiaoou \\\"></i>\\r\\n                <div class=\\\"left_title lh30\\\" id=\\\"m_robot_btn2\\\">平台客服</div>\\r\\n            </a>\\r\\n        </li>\\r\\n        <li class=\\\"guess hot_cur_question\\\">\\r\\n            <a href=\\\"/noauth/helpcenter/index\\\">\\r\\n                <i class=\\\"icon iconfont icon-bangzhuzhongxin \\\"></i>\\r\\n                <div class=\\\"left_title lh28\\\" id=\\\"question_help_left_title\\\">帮助中心</div>\\r\\n            </a>\\r\\n            <div class=\\\"question-help\\\">\\r\\n                <div id=\\\"hot_cur_question_list\\\" class=\\\"left_title hot_cur_question_list hide\\\">\\r\\n                    <script id=\\\"question_list_temp\\\" type=\\\"text/html\\\">\\r\\n                        <dl class=\\\"guess_con\\\">\\r\\n                            <dd>猜你想问：</dd>\\r\\n                            {{if data && data.length > 0}}\\r\\n                            {{each data as value index}}\\r\\n                            <dt><a href=\\\"{{value.questionUrl}}\\\" target=\\\"_blank\\\">{{value.questionName}}</a></dt>\\r\\n                            {{/each}}\\r\\n                            {{/if}}\\r\\n                        </dl>\\r\\n                    </script>\\r\\n                </div>\\r\\n            </div>\\r\\n        </li>\\r\\n        <script id=\\\"download_temp\\\" type=\\\"text/html\\\">\\r\\n            {{if download}}\\r\\n                {{if bid_download}}\\r\\n                      <li>\\r\\n                            <a href=\\\"javascript:;\\\" id=\\\"m_download_bid_resource_list\\\">\\r\\n                                <i class=\\\"icon iconfont icon-xiazaiziyuandan\\\"></i>\\r\\n                                <div class=\\\"left_title lh28\\\" id=\\\"m_download_bid_resource_list2\\\">下载资源单</div>\\r\\n                            </a>\\r\\n                      </li>\\r\\n                {{else}}\\r\\n                    <li>\\r\\n                        <a href=\\\"javascript:;\\\" id=\\\"m_download_resource_list\\\">\\r\\n                            <i class=\\\"icon iconfont icon-xiazaiziyuandan\\\"></i>\\r\\n                            <div class=\\\"left_title lh28\\\" id=\\\"m_download_resource_list2\\\">下载资源单</div>\\r\\n                        </a>\\r\\n                    </li>\\r\\n                {{/if}}\\r\\n            {{/if}}\\r\\n        </script>\\r\\n        <li class=\\\"shopping pb3\\\">\\r\\n            <a href=\\\"/buyer-ng/cart/myCart\\\" target=\\\"_blank\\\">\\r\\n                <i class=\\\"icon iconfont\\\"></i>\\r\\n                <em class=\\\"sidebar_small_bg\\\" id=\\\"global_sidebar_cart_number\\\">0</em>\\r\\n                <div class=\\\"left_title lh28\\\">购物车</div>\\r\\n            </a>\\r\\n        </li>\\r\\n        <li class=\\\"message\\\" onmouseover=\\\"$('.message-box').show()\\\" onmouseout=\\\"$('.message-box').hide()\\\">\\r\\n            <a href=\\\"/auth/message\\\" target=\\\"_blank\\\">\\r\\n                <i class=\\\"icon iconfont icon-xiaoxiqipao\\\"></i>\\r\\n                <em class=\\\"sidebar_small_bg\\\" id=\\\"message_amount\\\">0</em>\\r\\n                <div class=\\\"left_title lh28\\\" id=\\\"message_left_title\\\">消息</div>\\r\\n            </a>\\r\\n            <div class =\\\"message_content\\\"></div>\\r\\n        </li>\\r\\n        <li class=\\\"app\\\">\\r\\n            <a href=\\\"/rc/analysisCenter/v2/index\\\" target=\\\"_blank\\\">\\r\\n                <i class=\\\"icon iconfont icon-fenxi\\\"></i>\\r\\n                <div class=\\\"left_title lh28\\\">分析中心</div>\\r\\n            </a>\\r\\n        </li>\\r\\n        <li class=\\\"app\\\">\\r\\n            <a href=\\\"/quality-center/qualityCert/toQualityCertCenter\\\" target=\\\"_blank\\\">\\r\\n                <i class=\\\"icon iconfont icon-zhibaoshus\\\"></i>\\r\\n                <div class=\\\"left_title lh28\\\">质保书中心</div>\\r\\n            </a>\\r\\n        </li>\\r\\n        <li class=\\\"app\\\">\\r\\n            <a href=\\\"https://www.ouyeel.com/skb-ng/\\\" target=\\\"_blank\\\">\\r\\n                <i class=\\\"icon iconfont icon-paihaotong\\\"></i>\\r\\n                <div class=\\\"left_title lh28\\\">知钢</div>\\r\\n            </a>\\r\\n        </li>\\r\\n        <li class=\\\"position_f\\\" style=\\\"bottom: 42px;\\\">\\r\\n            <a href=\\\"/buyer-ng/complaintMenu/complainOpinion\\\" target=\\\"_blank\\\" class=\\\"\\\">\\r\\n                <i class=\\\"icon iconfont\\\"></i>\\r\\n                <div class=\\\"left_title lh28\\\" id=\\\"\\\">用户反馈</div>\\r\\n            </a>\\r\\n        </li>\\r\\n        <!-- ISSTS-14160 去掉app--->\\r\\n        <!-- <li class=\\\"mycode position_f\\\">\\r\\n            <a href=\\\"javascript:\\\"><i class=\\\"icon iconfont\\\"></i></a>\\r\\n            <div class=\\\"left_title code_me\\\">\\r\\n                <img id=\\\"EwmId\\\" src=\\\"http://cdn-ng.ouyeel.com/statics/home/assets/images/Ewm.png\\\">\\r\\n            </div>\\r\\n        </li> -->\\r\\n\\r\\n        <li class=\\\"assist_pop_question position_f\\\">\\r\\n            <a id=\\\"assist_pop_question_a\\\" href=\\\"javascript:void(0)\\\"><span class=\\\"iconfont icon-wenjuantiaocha\\\"></span></a>\\r\\n            <div class=\\\" left_title mark_assist\\\">\\r\\n                <div class=\\\"assist_txt wqContent\\\" >\\r\\n                    “欧冶服务，您说了算” <br>请填写2020年客户满意度调查问卷\\r\\n                </div>\\r\\n                <div class=\\\"btn_area\\\">\\r\\n                    <a href=\\\"/home-ng/question/question-naire\\\" id=\\\"question_ndwj\\\">参与调查</a>\\r\\n                </div>\\r\\n            </div>\\r\\n            <div class=\\\"ssist_popup_pa hide\\\">\\r\\n                <a href=\\\"javascript:void(0)\\\" class=\\\"a_btn_bd\\\" id=\\\"bztc_btn\\\">不再弹出</a>\\r\\n                <div class=\\\"wqContent\\\">\\r\\n                    “欧冶服务，您说了算” <br>请填写2020年客户满意度调查问卷\\r\\n                </div>\\r\\n                <div class=\\\"btn_area tc\\\">\\r\\n                    <a href=\\\"javascript:void(0)\\\"  id=\\\"ndwq\\\">年度问卷</a>\\r\\n                    <div class=\\\"btn_link\\\"><a href=\\\"javascript:void(0)\\\"  id=\\\"yhzs_btn\\\">以后再说</a></div>\\r\\n                </div>\\r\\n            </div>\\r\\n        </li>\\r\\n    </ul>\\r\\n\\r\\n\\r\\n</div>\\r\\n\\r\\n<div class=\\\"tucao_w warp\\\" id=\\\"div_question\\\" style=\\\"border: none; z-index: 100000001; top: 100px; display: none;\\\">\\r\\n</div>\\r\\n<div class=\\\"tucao_w warp\\\" id=\\\"div_question1\\\" style=\\\"border: none; z-index: 100000001; top: 100px; display: none;\\\">\\r\\n    <div class=\\\"zhezhao\\\" style=\\\"border:none;z-index:100000001;\\\"></div>\\r\\n    <div class=\\\"tucao_w_bg\\\" style=\\\"border:none;z-index:100000001;\\\">\\r\\n        <a class=\\\"close\\\" id=\\\"roast_close\\\">X</a>\\r\\n        <form id=\\\"question_form\\\">\\r\\n            <div class=\\\"title tc\\\">用户反馈</div>\\r\\n            <div class=\\\"font12 text\\\">\\r\\n                <div>尊敬的用户：</div>\\r\\n                <div style=\\\"text-indent: 24px\\\">对平台操作还满意吗？ </div>\\r\\n                <div style=\\\"text-indent: 24px\\\">为了向您提供更好的服务，我们希望收集您的宝贵看法和建议，收到反馈后我们会及时联系您，并对采纳的意见给予相应的奖励，感谢您的支持!</div>\\r\\n            </div>\\r\\n            <div class=\\\"content\\\">\\r\\n                <div class=\\\"font12\\\">\\r\\n                    <label class=\\\"fb\\\"><em class=\\\"red\\\">*</em>姓名：</label> <input type=\\\"text\\\" width=\\\"120px;\\\" name=\\\"userName\\\" value=\\\"\\\">\\r\\n                    <label class=\\\"fb ml30\\\"><em class=\\\"red\\\">*</em>联系方式：</label><input type=\\\"text\\\" name=\\\"mobile\\\" width=\\\"120px;\\\" value=\\\"\\\">\\r\\n                </div>\\r\\n                <div class=\\\"mt10\\\">\\r\\n                    <textarea placeholder=\\\"请留下您宝贵的意见\\\" name=\\\"content\\\" style=\\\"width: 496px; max-width: 496px; height: 92px; margin: 0px;resize:none;\\\"></textarea>\\r\\n                </div>\\r\\n                <a class=\\\"btn_submit\\\" id=\\\"div_question_submit\\\" href=\\\"javascript:\\\">提交</a>\\r\\n            </div>\\r\\n        </form>\\r\\n    </div>\\r\\n</div>\\r\\n\\r\\n<div class=\\\"tucao_w warp\\\" id=\\\"div_question2\\\" style=\\\"border: none; z-index: 100000001; top: 100px;display:none;\\\">\\r\\n    <div class=\\\"zhezhao\\\" style=\\\"border:none;z-index:100000001;\\\"></div>\\r\\n    <div class=\\\"tucao_w_bg\\\" style=\\\"border:none;z-index:100000001;background:url(https://cdn-ng.ouyeel.com/statics/roast/images/live_question3.png) no-repeat;height:508px;\\\">\\r\\n        <a class=\\\"close\\\" id=\\\"roast_close\\\">X</a>\\r\\n        <form id=\\\"question_form\\\">\\r\\n            <div class=\\\"title tc\\\">用户反馈</div>\\r\\n            <div class=\\\"font12 text\\\">\\r\\n                <div>尊敬的用户：</div>\\r\\n                <div style=\\\"text-indent: 24px\\\">对平台操作还满意吗？ </div>\\r\\n                <div style=\\\"text-indent: 24px\\\">为了向您提供更好的服务，我们希望收集您的宝贵看法和建议，收到反馈后我们会及时联系您，并对采纳的意见给予相应的奖励，感谢您的支持!</div>\\r\\n            </div>\\r\\n            <div class=\\\"content\\\">\\r\\n                <div class=\\\"font12 pt15\\\">\\r\\n                    <label class=\\\"fb\\\">　　<em class=\\\"red\\\">*</em>姓名：</label> <input type=\\\"text\\\" width=\\\"120px;\\\" name=\\\"userName\\\" value=\\\"\\\">\\r\\n                    <label class=\\\"fb ml30\\\"><em class=\\\"red\\\">*</em>联系方式：</label><input type=\\\"text\\\" name=\\\"mobile\\\" width=\\\"120px;\\\" value=\\\"\\\">\\r\\n                </div>\\r\\n                <div class=\\\"font12 pt15\\\">\\r\\n                   <label class=\\\"fb\\\"><em class=\\\"red\\\">*</em>问题类型：</label>\\r\\n                   <span class=\\\"sui-dropdown dropdown-bordered select\\\">\\r\\n                       <span class=\\\"dropdown-inner\\\">\\r\\n                           <a id=\\\"drop1\\\" role=\\\"button\\\" data-toggle=\\\"dropdown\\\" href=\\\"#\\\" class=\\\"dropdown-toggle\\\" style=\\\"width:145px\\\">\\r\\n                           <input  name=\\\"adviceType\\\" type=\\\"hidden\\\"><i class=\\\"caret\\\"></i><span>请选择</span>\\r\\n                   </a>\\r\\n                   <ul id=\\\"menu1\\\" role=\\\"menu\\\" aria-labelledby=\\\"drop1\\\" class=\\\"sui-dropdown-menu\\\">\\r\\n                       <li role=\\\"presentation\\\"><a role=\\\"menuitem\\\" tabindex=\\\"-1\\\" href=\\\"javascript:void(0);\\\" value=\\\"10\\\">搜不到资源</a></li>\\r\\n                       <li role=\\\"presentation\\\"><a role=\\\"menuitem\\\" tabindex=\\\"-1\\\" href=\\\"javascript:void(0);\\\" value=\\\"20\\\">搜索结果与条件不符</a></li>\\r\\n                       <li role=\\\"presentation\\\"><a role=\\\"menuitem\\\" tabindex=\\\"-1\\\" href=\\\"javascript:void(0);\\\" value=\\\"30\\\">搜索词解析错误</a></li>\\r\\n                   </ul>\\r\\n                   </span>\\r\\n                   </span>\\r\\n                </div>\\r\\n                <div class=\\\"mt10\\\">\\r\\n                    <textarea placeholder=\\\"请留下您宝贵的意见\\\" name=\\\"content\\\" style=\\\"width: 496px; max-width: 496px; height: 92px; margin: 0px;resize:none;\\\">搜索结果不准确，请改进。（请补充详细问题描述）</textarea>\\r\\n                </div>\\r\\n                <a class=\\\"btn_submit\\\" id=\\\"div_question_submit\\\" href=\\\"javascript:\\\">提交</a>\\r\\n            </div>\\r\\n        </form>\\r\\n    </div>\\r\\n</div>\"},\"time\":1742350277963,\"expire\":86400000}",
    "sortBar_ModeChangefalse": "false",
    "__#classType": "localStorage",
    "sortBar_service_mode_change_isCommodityfalse": "resource",
    "$_YWTU": "ZduBX6I2eRSfd6Y2uOvrqX45yogORlFVoJyM0JaBodW",
    "olderVersion": "1741257013505",
    "$_YVTX": "Ws9"
}
sessionStorage={
    "$_YWTU": "ZduBX6I2eRSfd6Y2uOvrqX45yogORlFVoJyM0JaBodW",
    "OY_isLogin": "{\"value\":false,\"timestamp\":1742350279300}",
    "$_YVTX": "Ws9"
}


// window.__proto__=Window.prototype;



//document环境
document = {
    appendChild : function (){
        // console.log("appendChild")
    },
    removeChild: function (){
        // console.log("removeChild")
    },
    createElement: function (arg) {
        console.log('document的createElement获取参数:', arg)
        if (arg === 'div') {
            return {
                style:{
                    visibility:'hidden',
                    position:'absolute',
                },
                getElementsByTagName: function (res) {
                    if (res === 'i') {
                        return []
                    } else {
                        console.log('argumentsError：' + 'div.getElementsByTagName' + '的参数应该是："' + res + '"。')
                    }
                },
                setAttribute: function (arg, arg1) {
                    console.log("div标签的setAttribute方法接受的参数====>",arg,arg1)
                },
            }
        }
        if(arg==="form"){
            return {}
        }
        if(arg==="input"){
            return {}
        }
        if(arg==="a"){
            return {}
        }
    },
    getElementsByTagName: function (arg) {
        console.log('document的getElementsByTagName获取参数:', arg)
        if (arg === 'meta') {
            return [
                {
                    'http-equiv': 'Content-Type',
                    content: 'text/html; charset=utf-8',
                    getAttribute: function (res) {
                        console.log('meta中getAttribute接收到的参数为：', res)
                    },
                },
                {
                    content: content,
                    parentNode: {
                        removeChild: function () {
                        }
                    },
                    getAttribute: function (res) {
                        console.log('meta中getAttribute接收到的参数为：', res)
                    },
                }
            ]
        } else if (arg === 'base') {
            return []
        } else if (arg === 'script') {
            return [
                {
                    type: 'text/javascript',
                    charset: 'iso-8859-1',
                    src: '/IkxfQuImHWbf/szBN0h1em4ON.87f8093.js',
                    r: 'm',
                    getAttribute: function (res) {
                        console.log('argumentsError：' + 'script[0].getAttribute' + '的参数应该是："' + res + '"。');
                        if (res === 'r') {
                            return "m"
                        } else {
                            console.log('argumentsError：' + 'script[0].getAttribute' + '的参数应该是："' + res + '"。')
                        }
                    },
                    parentElement: {
                        removeChild: function () {
                        }
                    },
                    parentNode: {
                        removeChild: function () {
                        }
                    }
                },
                {
                    type: 'text/javascript',
                    r: 'm',
                    getAttribute: function (res) {
                        console.log('argumentsError：' + 'script[1].getAttribute' + '的参数应该是："' + res + '"。');
                        if (res === 'r') {
                            return "m"
                        } else {
                            console.log('argumentsError：' + 'script[1].getAttribute' + '的参数应该是："' + res + '"。')
                        }
                    },
                    parentElement: {
                        removeChild: function () {
                        }
                    }
                },
                // {
                //     getAttribute: function (res) {
                //         console.log('argumentsError：' + 'script[0].getAttribute' + '的参数应该是："' + res + '"。');
                //         if (res === 'r') {
                //             return "m"
                //         }
                //     },
                //     parentElement: {
                //         removeChild: function (arg) {
                //             console.log('script的parentElement的removeChild接受的参数:', arg);
                //         }
                //     },
                //     parentNode: {
                //         removeChild: function (arg) {
                //             console.log('script的parentNode的removeChild接受的参数:', arg);
                //         }
                //     },
                // },
                // {
                //     getAttribute: function (res) {
                //         console.log('argumentsError：' + 'script[1].getAttribute' + '的参数应该是："' + res + '"。');
                //         if (res === 'r') {
                //             return "m"
                //         }
                //     },
                //     parentElement: {
                //         removeChild: function (arg) {
                //             console.log('script的parentElement的removeChild接受的参数:', arg);
                //         }
                //     },
                //     parentNode: {
                //         removeChild: function (arg) {
                //             console.log('script的parentNode的removeChild接受的参数:', arg);
                //         }
                //     },
                // },
            ]
        }
    },
    getElementById: function (arg) {
        console.log('document的getElementById获取参数:', arg)
    },
    addEventListener: function () {
        console.log('document的addEventListener获取参数:', arguments)
    },
    attachEvent: function () {
        console.log('document的attachEvent获取参数:', arguments)
    },
    documentElement: watch({
        style:{},
        getAttribute: function () {
            console.log('document.documentElement的getAttribute获取参数:', arguments)
        },
        addEventListener: function () {
            console.log('document.documentElement的addEventListener获取参数:', arguments)
        },
        attachEvent: function () {
            console.log('document.documentElement的attachEvent获取参数:', arguments)
        },
    },"document.documentElement====>"),
    all:{
        length:0,
    },
    // visibilityState:"visible",
}


location={
    "ancestorOrigins": {},
    "href": "http://www.nhc.gov.cn/wjw/xinw/xwzx.shtml",
    "origin": "http://www.nhc.gov.cn",
    "protocol": "http:",
    "host": "www.nhc.gov.cn",
    "hostname": "www.nhc.gov.cn",
    "port": "",
    "pathname": "/rs5/xinw/xwzx.shtml",
    "search": "",
    "hash": ""
}

navigator={
    appCodeName: "Mozilla",
    appName: "Netscape",
    appVersion: "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    cookieEnabled: true,
    doNotTrack: null,
    hardwareConcurrency: 12,
    language: "zh-CN",
    languages:["zh-CN", "zh"],
    maxTouchPoints: 0,
    onLine: true,
    pdfViewerEnabled: true,
    platform: "Win32",
    plugins: {
        length: 4,
        [Symbol.toStringTag]:'PluginArray',
        0:{
            name:'PDF Viewer',
            [Symbol.toStringTag]:'Plugin',
            length:2
        },
        1:{
            name:'ff_ss',
            [Symbol.toStringTag]:'Plugin',
            length:2
        },
        2:{
            name:'ss_ff',
            [Symbol.toStringTag]:'Plugin',
            length:2
        },
        3:{
            name:'FFloveSS',
            [Symbol.toStringTag]:'Plugin',
            length:2
        },
    },
    product: "Gecko",
    productSub: "20030107",
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    vendor: "Google Inc.",
    vendorSub: "",
    webdriver: false,
    mimeTypes: {
    "0": {},
    "1": {},
   "application/pdf": {
        description:"Portable Document Format",
        suffixes: "pdf",
        type:"application/pdf"
   },
   "text/pdf": {},
},
};
history={};
screen={};

setTimeout=function () {}
setInterval=function () {}

get_enviroment(proxy_array)
//导入ts和解析ts的自执行方法

require('./rs_ts');
require('./rs_func');

function get_cookie() {
    ck=document.cookie;
    ck_length=ck.split(';')[0].split('=')[1].length;
    console.log('cookie长度=======>',ck_length);
    return ck;
}
console.log(get_cookie());
// console.log(localStorage);
// console.log(sessionStorage);





