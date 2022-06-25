<?php
header("Content-type: text/html; charset=utf-8");



if (!(isset($_GET['url']))) {
	exit ("缺少参数");
}
if (!(isset($_GET['ruby']))) {
	$_GET['ruby'] = 0;
}

if (strpos($_GET['url'],'j-lyric')) {
	getjlyric($_GET['url']);
}
if (strpos($_GET['url'],'uta-net')) {
	getuta_net($_GET['url']);
}
if (strpos($_GET['url'],'utaten')) {
	getutaten($_GET['url'],$_GET['ruby']);
}

function getjlyric($url) {
	//获取源码
	$jlyricraw = file_get_contents($url);
	//获取歌词主体
	$patterna = '/<p id="Lyric">.+?<\/p>/';
	preg_match($patterna,$jlyricraw,$matcha);
	$jlyric = $matcha[0];
	//获取歌手作词作曲信息
	$patternb = '/<p class="sml">.+?<\/p>/';
	preg_match_all($patternb,$jlyricraw,$matchb);
	$info = $matchb[0][0].$matchb[0][1].$matchb[0][2];
	$info = preg_replace('/<.+?>/','',$info);
	$info = str_replace("作詞：",'<br>作詞：',$info);
	$info = str_replace("作曲：",'<br>作曲：',$info);
	//输出
	echo $info . $jlyric;
	}

function getuta_net($url) {
	//获取源码
	$uta_netraw = file_get_contents($url);
	//获取歌词主体
	$patterna = '/<div id="kashi_area".+<\/div>/';
	preg_match($patterna,$uta_netraw,$matcha);
	$uta_net = $matcha[0];
	//获取歌手作词作曲信息
	$patternb = '/歌手：.+<\/h4>/';
	preg_match($patternb,$uta_netraw,$matchb);
	$info = $matchb[0];
	$info = preg_replace('/<.+?>/','',$info);
	$info = str_replace("作詞：",'<br>作詞：',$info);
	$info = str_replace("作曲：",'<br>作曲：',$info).'<br><br>';
	//输出
	echo $info . $uta_net;
}

function getutaten($url,$ruby) {
	//获取源码
	$jlyricraw = file_get_contents($url);

	//获取歌词主体
	if ($ruby != 3 and $ruby != 4)
	{
		$patterna = '/<div class="lyricBody ">.*?<\/div>/is';
		preg_match($patterna,$jlyricraw,$matcha);
		$jlyric = $matcha[0];
		$jlyric = str_replace("<br />",'#换行符#',$jlyric);
		$jlyric = preg_replace('/( ) {5,10}/','',$jlyric);		
	}else{
		$patterna = '/<div class="romaji".*?<\/div>/is';
		preg_match($patterna,$jlyricraw,$matcha);
		$jlyric = $matcha[0];
		$jlyric = str_replace("<br />",'#换行符#',$jlyric);
		$jlyric = preg_replace('/( ) {5,10}/','',$jlyric);
	}

	
	//注音样式选择
	switch ($ruby)
	{
		//删除注音
		case 0:
		$jlyric = preg_replace('/<span class="rt">.+?<\/span>/','',$jlyric);
		break; 
		
		//样式 汉字(注音)
		case 1:
		$jlyric = str_replace('<span class="rt">','(',$jlyric);
		$jlyric = str_replace('</span></span>',')',$jlyric);
		break; 
		
		//样式 (汉字,注音)
		case 2:
		$jlyric = str_replace('<span class="rb">','(',$jlyric);
		$jlyric = str_replace('</span><span class="rt">',',',$jlyric);
		$jlyric = str_replace('</span></span>',')',$jlyric);		
		break;

		//样式 汉字(罗马音)
		case 3:
		$jlyric = str_replace('<span class="rt">','(',$jlyric);
		$jlyric = str_replace('</span></span>',')',$jlyric);
		break; 
		
		//样式 (汉字,罗马音)
		case 4:
		$jlyric = str_replace('<span class="rb">','(',$jlyric);
		$jlyric = str_replace('</span><span class="rt">',',',$jlyric);
		$jlyric = str_replace('</span></span>',')',$jlyric);		
		break;
		
		//参数错误，无1-3，默认不带注音
		default:
		//echo "ERR";
		$jlyric = preg_replace('/<span class="rt">.+?<\/span>/','',$jlyric);
		}		
	
	$jlyric = preg_replace('/<.+?>/','',$jlyric);
	$jlyric = str_replace("#换行符#",'<br>',$jlyric);	

	/*获取歌手作词作曲信息
	曲名+歌手*/
	$patternb = '/<h1.*?<\/h1>/is';//190923修复改版bug；<h1>.*?<\/h1>改为<h1.*?<\/h1>
	preg_match($patternb,$jlyricraw,$matchb);//初始信息
	$info = preg_replace('/( ) {5,10}/','',$matchb[0]);//去除空格
	preg_match('/「.+」/',$info,$matchc);//曲名
	$quming = $matchc[0];
	preg_match('/.+<\/a>/',$info,$matchc);//歌手
	$geshou = str_replace('</a>','',$matchc[0]);

	//作词+作曲
	$patternc = '/作.*作曲.*?dd>/is';
	preg_match($patternc,$jlyricraw,$matchc);//初始信息
	preg_match_all('/<dd.+?dd>/',$matchc[0],$matchd);//多次匹配作词作曲
	$zuoci = preg_replace('/<.+?>/','',$matchd[0][0]);//作词
	$zuoqu = preg_replace('/<.+?>/','',$matchd[0][1]);//作曲

	$info = '曲名：'. $quming . '<br>歌手：' . $geshou . '<br>作詞：' . $zuoci . '<br>作曲：' . $zuoqu . '<br><br>';
	//输出
	echo $info . $jlyric;
	}
print( getElementById( $result , 'lyric' ) );
?>