(function () {
  'use strict';
  var form = document.getElementById('website-feedback-form');
  if (!form) return;
  var category = document.getElementById('website-feedback-category');
  var result = document.getElementById('website-feedback-result');
  var submitButton = document.getElementById('website-feedback-submit');
  var endpoint = 'https://api.dupontmaster.com/api/feedback';
  var busy = false;

  document.querySelectorAll('[data-feedback-category]').forEach(function (link) {
    link.addEventListener('click', function () {
      var requested = link.getAttribute('data-feedback-category');
      if (requested && category.querySelector('option[value="' + requested + '"]')) {
        category.value = requested;
      }
    });
  });

  var changeResult = function (message, type) {
    result.textContent = message;
    result.setAttribute('data-type', type || 'info');
  };

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    if (busy) return;
    changeResult('', 'info');
    if (!form.reportValidity()) return;

    var content = document.getElementById('website-feedback-content').value.trim();
    if (content.length < 10 || content.length > 3000) {
      changeResult('请将反馈内容填写为 10–3000 字。', 'error');
      return;
    }
    var controller = new AbortController();
    var timeout = window.setTimeout(function () { controller.abort(); }, 15000);
    busy = true;
    submitButton.disabled = true;
    submitButton.textContent = '正在提交…';
    try {
      var response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          category: category.value,
          content: content,
          phone: document.getElementById('website-feedback-phone').value.trim(),
          email: document.getElementById('website-feedback-email').value.trim(),
          consent: form.elements.consent.checked,
          website: form.elements.website.value,
          source: 'www.dupontmaster.com',
        }),
      });
      var payload = await response.json().catch(function () { return {}; });
      if (!response.ok || !payload.ok) throw new Error(payload.error || '暂时无法提交反馈，请稍后再试');
      form.reset();
      changeResult(
        payload.emailSent
          ? '反馈已保存，邮件通知已发送。感谢你的建议！反馈编号：' + (payload.reference || '')
          : '反馈已保存，编号：' + (payload.reference || '') + '。目前邮件通知尚未完成，但管理员可以查看你的反馈。',
        'success'
      );
    } catch (error) {
      changeResult(error && error.name === 'AbortError'
        ? '提交超时，请检查网络后重试。'
        : (error && error.message) || '提交失败，请稍后再试。', 'error');
    } finally {
      window.clearTimeout(timeout);
      busy = false;
      submitButton.disabled = false;
      submitButton.textContent = '发送反馈';
    }
  });
})();
