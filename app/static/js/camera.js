var g_nIndex = 0;
function OnBtnRefresh() {
        document.getElementById("imgDisplay").src = "/jpeg?_="+g_nIndex;
        g_nIndex = g_nIndex + 1;
}

function OnImgLoad() {
        setTimeout("OnBtnRefresh()",50);
}


