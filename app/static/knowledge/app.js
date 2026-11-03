"use strict";
const $ = id => document.getElementById(id);
let documents = [], currentDocument = null, currentPolicy = null;
function notice(text, error = false) { $("notice").textContent = text; $("notice").className = error ? "error" : ""; }
async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if ($("token").value) headers.set("Authorization", "Bearer " + $("token").value);
  if (options.body && typeof options.body === "string") headers.set("Content-Type", "application/json");
  const response = await fetch("/knowledge" + path, {...options, headers});
  if (!response.ok) { let value; try { value = await response.json(); } catch { value = {detail: response.statusText}; } throw Error(typeof value.detail === "string" ? value.detail : JSON.stringify(value.detail)); }
  return response.json();
}
async function run(work) { try { await work(); } catch (error) { notice(error.message, true); } }
function node(tag, text, className) { const e = document.createElement(tag); if (text !== undefined) e.textContent = text; if (className) e.className = className; return e; }
function button(text, action, danger = false) { const e = node("button", text, danger ? "danger" : ""); e.type = "button"; e.onclick = () => run(action); return e; }
function localTime(value) { if (!value) return ""; const d = new Date(value); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0,16); }
function utc(id) { return $(id).value ? new Date($(id).value).toISOString() : null; }
async function refresh() {
  const [status, docs, policy, history] = await Promise.all([api("/status"),api("/documents"),api("/policy"),api("/generations")]);
  documents = docs; currentPolicy = policy;
  $("summary").textContent = `${docs.filter(d=>!d.purged_at).length} 份文档 · 当前发布 ${status.current?.generation?.slice(0,12) || "无"} · ${status.manifest?.counts?.children || 0} 个检索块`;
  $("documents").replaceChildren();
  for (const d of docs) {
    const tr = node("tr"), name = node("td"), state = node("td"), views = node("td"), actions = node("td");
    name.append(node("strong",d.purge_state === "completed" ? "已硬删除文档" : d.source_path.split(/[\\/]/).pop()),node("small",`${d.metadata.category || "未分类"} / ${d.metadata.domain || "未设置领域"}`),node("small",d.document_id));
    const selected = d.selected_version_id || d.latest_version_id;
    state.append(node("span",d.purged_at ? (d.purge_state === "completed" ? "已彻底清除" : "已停止提供，清理尚未完成") : d.deleted_at ? "已软删除" : d.needs_build ? "待构建发布" : "已发布"),node("small",`内容版本 ${d.versions.find(v=>v.version_id===selected)?.version_number || "—"}${d.selected_version_id ? "（固定历史版本）" : ""}`));
    views.append(node("span",d.view_config.enabled ? "已启用" : "关闭"),node("small",`${d.view_states[0]?.status || "尚未生成"} · 已发布 ${d.published_view_count || 0} 个`));
    if (!d.purged_at) {
      actions.append(button("详情 / 设置",()=>openEditor(d)),button(d.deleted_at ? "取消删除" : "软删除",async()=>{await api(`/documents/${d.document_id}${d.deleted_at?"/restore":""}`,{method:d.deleted_at?"POST":"DELETE"});await refresh();}));
      actions.append(button("更新内容",()=>updateFile(d)));
      actions.append(button("硬删除",async()=>{if (!confirm("不可恢复：清除受管理原文、版本与派生产物，并撤销含此文档的历史快照。应用外备份不在范围内。确定？"))return; await api(`/documents/${d.document_id}/purge`,{method:"DELETE",body:JSON.stringify({confirm:true})});await refresh();notice("硬删除完成。");},true));
    } else if (d.purge_state !== "completed") {
      actions.append(button("继续硬删除清理",async()=>{if(!confirm("继续不可恢复的硬删除清理？已停止提供的内容不会恢复。"))return;await api(`/documents/${d.document_id}/purge`,{method:"DELETE",body:JSON.stringify({confirm:true})});await refresh();notice("硬删除清理完成。");},true));
    }
    tr.append(name,state,views,actions);$("documents").append(tr);
  }
  $("strategy").value=policy.default_strategy;$("multiview").checked=policy.multi_view_enabled;$("reranker-model").value=policy.reranker_model;$("reranker-timeout").value=policy.reranker_timeout_seconds;
  $("jobs").textContent=JSON.stringify(status.jobs,null,2);$("generations").replaceChildren();
  for(const generation of history.generations) {
    const row=node("div",undefined,"generation");row.append(node("code",generation.generation_id.slice(0,12)),node("span",generation.current?"当前发布":generation.healthy?"可用快照":"不可用"),node("small",generation.created_at||""));
    if(!generation.current && generation.healthy)row.append(button("回滚至此快照",async()=>{if(!confirm("发布此历史快照？当前软删除、有效期与硬删除限制仍会生效。"))return;await api("/rollback/"+generation.generation_id,{method:"POST"});await refresh();}));
    $("generations").append(row);
  }
  if(status.last_build_error) notice(status.last_build_error,true);
}
function openEditor(d) {
  currentDocument=d;$("editor").hidden=false;$("editor-title").textContent="文档设置 · "+d.source_path.split(/[\\/]/).pop();
  $("category").value=d.metadata.category||"";$("domain").value=d.metadata.domain||"";$("source").value=d.metadata.source||"";
  $("view-model").value=d.view_config.model||"";$("view-enabled").checked=!!d.view_config.enabled;$("view-failure").value=d.view_config.failure_policy||"publish_without_views";
  $("effective").value=localTime(d.effective_at);$("expires").value=localTime(d.expires_at);$("versions").replaceChildren();
  for(const v of [...d.versions].reverse()){const o=node("option",`版本 ${v.version_number} · ${v.created_at} · ${v.content_hash.slice(0,12)}`);o.value=v.version_id;$("versions").append(o);}
  $("versions").value=d.selected_version_id||d.latest_version_id;$("editor").scrollIntoView({behavior:"smooth"});
}
async function upload(file,d) { if(!file)throw Error("请先选择文件");await api(`/documents?filename=${encodeURIComponent(file.name)}${d?"&document_id="+d.document_id:""}`,{method:"POST",body:file});await refresh();notice("内容已保存，构建发布后用于检索。"); }
function updateFile(d){const input=node("input");input.type="file";input.onchange=()=>run(()=>upload(input.files[0],d));input.click();}
$("refresh").onclick=()=>run(refresh);$("upload").onclick=()=>run(()=>upload($("upload-file").files[0]));
$("build").onclick=()=>run(async()=>{if(documents.some(d=>!d.deleted_at&&d.view_config.enabled)&&!confirm("启用 View 的文档可能产生模型调用费用；服务端会限制请求数。继续构建？"))return;await api("/build",{method:"POST"});notice("构建已提交，旧发布继续服务。稍后刷新查看任务结果。");});
$("close-editor").onclick=()=>{$("editor").hidden=true;};
$("settings").onsubmit=e=>{e.preventDefault();run(async()=>{if($("view-enabled").checked&&!currentDocument.view_config.enabled&&!confirm("允许离线构建为此文档调用生成模型？可能产生费用。"))return;await api(`/documents/${currentDocument.document_id}`,{method:"PATCH",body:JSON.stringify({metadata:{...currentDocument.metadata,category:$("category").value,domain:$("domain").value,source:$("source").value},view_config:{...currentDocument.view_config,enabled:$("view-enabled").checked,model:$("view-model").value||null,failure_policy:$("view-failure").value}})});await api(`/documents/${currentDocument.document_id}/validity`,{method:"PUT",body:JSON.stringify({effective_at:utc("effective"),expires_at:utc("expires")})});await refresh();openEditor(documents.find(d=>d.document_id===currentDocument.document_id));notice("设置已保存。View 改动需构建发布，有效期即时限制在线检索。");});};
$("restore-version").onclick=()=>run(async()=>{if(!confirm("选择该历史内容版本，并在下次构建发布时生效？"))return;await api(`/documents/${currentDocument.document_id}/restore-version`,{method:"POST",body:JSON.stringify({version_id:$("versions").value})});await refresh();notice("已选择历史版本，请构建发布。");});
$("download").onclick=()=>run(async()=>{const headers={};if($("token").value)headers.Authorization="Bearer "+$("token").value;const response=await fetch(`/knowledge/documents/${currentDocument.document_id}/source?version_id=${$("versions").value}`,{headers});if(!response.ok)throw Error("原文下载失败");const url=URL.createObjectURL(await response.blob()),a=node("a");a.href=url;a.download=currentDocument.source_path.split(/[\\/]/).pop();a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$("policy").onsubmit=e=>{e.preventDefault();run(async()=>{currentPolicy=await api("/policy",{method:"PUT",body:JSON.stringify({...currentPolicy,default_strategy:$("strategy").value,multi_view_enabled:$("multiview").checked,reranker_model:$("reranker-model").value,reranker_timeout_seconds:Number($("reranker-timeout").value)})});notice("检索策略已保存，无需重建文档。");});};
$("search").onsubmit=e=>{e.preventDefault();run(async()=>{const parameters=new URLSearchParams({q:$("query").value,k:"3",include_trace:"true",supplement:String($("supplement").checked)});if($("as-of").value)parameters.set("as_of",utc("as-of"));const result=await api("/search?"+parameters);$("results").replaceChildren();for(const item of result.results){const article=node("article",undefined,"evidence");article.append(node("strong",item.source_name||item.filename||item.document_id),node("small",`版本 ${item.version_id||"—"} · 页 ${item.page_start||"—"} · ${item.parent_id}`),node("pre",item.content));$("results").append(article);}if(!result.results.length)$("results").textContent="没有检索结果。这不等于业务事实不存在。";$("trace").textContent=JSON.stringify(result.trace,null,2);notice("检索完成。");});};
$("gc").onclick=()=>run(async()=>{if(!confirm("清理宽限期已过且不受保护的旧快照？清理后的时间点将不能再查询。"))return;const result=await api("/gc",{method:"POST"});await refresh();notice(`清理 ${result.generations.length} 个旧快照。`);});
run(refresh);
