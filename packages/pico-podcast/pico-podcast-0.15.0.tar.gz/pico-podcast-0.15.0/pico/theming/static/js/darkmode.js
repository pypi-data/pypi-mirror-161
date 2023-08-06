// =====================
// Dark Mode Toogle 🌒 ☀️ - Inspired by:
// https://hankchizljaw.com/wrote/create-a-user-controlled-dark-or-light-mode/
// =====================

var user_color_scheme = localStorage.getItem('user-color-scheme');

function initial_mode_set(mode) {
    if (mode) {
        document.documentElement.setAttribute('data-user-color-scheme', mode);
    }
}

initial_mode_set(user_color_scheme);

window.addEventListener('DOMContentLoaded', (event) => {
    var STORAGE_KEY = 'user-color-scheme';
    var COLOR_MODE_KEY = '--color-mode';
    var modeToggleButton = document.querySelector('.js-mode-toggle');
    var modeToggleText = document.querySelector('.js-mode-toggle-text');
    var modeToggleTitle = document.querySelector('.js-mode-toggle-title');

    var getCSSCustomProp = function getCSSCustomProp(propKey) {
        var response = getComputedStyle(document.documentElement).getPropertyValue(propKey);

        if (response.length) {
            response = response.replace(/\"/g, '').trim();
        }

        return response;
    };

    var applySetting = function applySetting(passedSetting) {
        var currentSetting = passedSetting || localStorage.getItem(STORAGE_KEY);

        if (currentSetting) {
            document.documentElement.setAttribute('data-user-color-scheme', currentSetting);
            setButtonLabelAndStatus(currentSetting);
        } else {
            setButtonLabelAndStatus(getCSSCustomProp(COLOR_MODE_KEY));
        }

        document.querySelectorAll('iframe[data-theme-param]').forEach(
            function (element) {
                var src = element.getAttribute('data-src');
                var param = element.getAttribute('data-theme-param');
                var url = src + '?' + param + '=' + currentSetting;

                element.src = url;
            }
        )
    };

    var setButtonLabelAndStatus = function setButtonLabelAndStatus(currentSetting) {
        modeToggleText.innerText = "Enable ".concat(currentSetting === 'dark' ? 'light' : 'dark', " mode");
        modeToggleTitle.title = "Enable ".concat(currentSetting === 'dark' ? 'light' : 'dark', " mode");
    };

    var toggleSetting = function toggleSetting() {
        var currentSetting = localStorage.getItem(STORAGE_KEY);

        switch (currentSetting) {
            case null:
                currentSetting = getCSSCustomProp(COLOR_MODE_KEY) === 'dark' ? 'light' : 'dark';
                break;

            case 'light':
                currentSetting = 'dark';
                break;

            case 'dark':
                currentSetting = 'light';
                break;
        }

        localStorage.setItem(STORAGE_KEY, currentSetting);
        return currentSetting;
    };

    modeToggleButton.addEventListener('click', function (evt) {
        evt.preventDefault();
        applySetting(toggleSetting());
    });

    applySetting();

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',
        function(e) {
            var newColorScheme = e.matches ? "dark" : "light";

            document.querySelectorAll('iframe[data-theme-param]').forEach(
                function (element) {
                    var src = element.getAttribute('data-src');
                    var param = element.getAttribute('data-theme-param');
                    var url = src + '?' + param + '=' + newColorScheme;

                    element.src = url;
                }
            )
        }
    );
});
