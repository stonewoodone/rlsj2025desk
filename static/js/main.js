// Main JavaScript file for the Fuel Settlement System

// Set active nav item based on current URL
document.addEventListener('DOMContentLoaded', function() {
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentLocation.includes(href) && href !== '/') {
            link.classList.add('active');
            
            // If it's a dropdown item, also set the parent dropdown as active
            const dropdownParent = link.closest('.dropdown');
            if (dropdownParent) {
                const dropdownToggle = dropdownParent.querySelector('.dropdown-toggle');
                if (dropdownToggle) {
                    dropdownToggle.classList.add('active');
                }
            }
        } else if (href === '/' && currentLocation === '/') {
            link.classList.add('active');
        }
    });
});

// Format numbers with commas for thousands
function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format currency
function formatCurrency(number) {
    return '¥ ' + formatNumber(parseFloat(number).toFixed(2));
}

// Format percentage
function formatPercentage(number) {
    return parseFloat(number).toFixed(2) + '%';
}

// Confirm delete
function confirmDelete(event, itemType) {
    if (!confirm(`确定要删除这个${itemType}吗？此操作不可撤销。`)) {
        event.preventDefault();
    }
}

// Supplier form: Auto-generate contract name based on supplier
function updateContractName() {
    const supplierSelect = document.getElementById('supplier_id');
    if (supplierSelect) {
        supplierSelect.addEventListener('change', function() {
            const supplierId = this.value;
            if (supplierId) {
                fetch(`/contracts/get_supplier_name/${supplierId}`)
                    .then(response => response.json())
                    .then(data => {
                        const contractNameInput = document.getElementById('contract_name');
                        if (contractNameInput && !contractNameInput.value) {
                            contractNameInput.value = data.full_name;
                        }
                    })
                    .catch(error => console.error('Error fetching supplier name:', error));
            }
        });
    }
}

// Contract form: Calculate mine unit price based on contract type and calorific value
function setupPriceCalculation() {
    const contractTypeSelect = document.getElementById('contract_type');
    const calorificValueInput = document.getElementById('mine_calorific_value');
    const unitPriceInput = document.getElementById('mine_unit_price');
    const contractNameInput = document.getElementById('contract_name');
    
    if (contractTypeSelect && calorificValueInput && unitPriceInput) {
        function calculatePrice() {
            const contractType = contractTypeSelect.value;
            const calorificValue = calorificValueInput.value;
            const contractName = contractNameInput ? contractNameInput.value : '';
            
            if (contractType && calorificValue) {
                const formData = new FormData();
                formData.append('contract_type', contractType);
                formData.append('calorific_value', calorificValue);
                formData.append('contract_name', contractName);
                
                fetch('/contracts/calculate_price', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.price !== null) {
                        unitPriceInput.value = data.price.toFixed(2);
                    } else {
                        // For manual input, don't auto-fill
                        if (!unitPriceInput.value) {
                            unitPriceInput.placeholder = '请手动输入矿发单价';
                        }
                    }
                })
                .catch(error => console.error('Error calculating price:', error));
            }
        }
        
        contractTypeSelect.addEventListener('change', calculatePrice);
        calorificValueInput.addEventListener('input', calculatePrice);
        if (contractNameInput) {
            contractNameInput.addEventListener('input', calculatePrice);
        }
    }
}

// Mine Delivery form: Auto-fill calorific value and unit price based on contract
function setupContractDetails() {
    const contractSelect = document.getElementById('fuel_contract_id');
    const calorificValueInput = document.getElementById('mine_calorific_value');
    const unitPriceInput = document.getElementById('mine_unit_price');
    
    if (contractSelect && calorificValueInput && unitPriceInput) {
        contractSelect.addEventListener('change', function() {
            const contractId = this.value;
            if (contractId) {
                fetch(`/mine_deliveries/get_contract_details/${contractId}`)
                    .then(response => response.json())
                    .then(data => {
                        calorificValueInput.value = data.mine_calorific_value;
                        unitPriceInput.value = data.mine_unit_price;
                    })
                    .catch(error => console.error('Error fetching contract details:', error));
            }
        });
    }
}

// Transportation form: Auto-fill transport quantity based on contract and transport type
function setupTransportQuantity() {
    const contractSelect = document.getElementById('fuel_contract_id');
    const transportTypeSelect = document.getElementById('transport_type');
    const quantityInput = document.getElementById('transport_quantity');
    
    if (contractSelect && transportTypeSelect && quantityInput) {
        function updateQuantity() {
            const contractId = contractSelect.value;
            const transportType = transportTypeSelect.value;
            
            if (contractId && transportType) {
                fetch(`/transportation/get_transport_quantity/${contractId}/${transportType}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.quantity > 0) {
                            quantityInput.value = data.quantity.toFixed(2);
                        }
                    })
                    .catch(error => console.error('Error fetching transport quantity:', error));
            }
        }
        
        contractSelect.addEventListener('change', updateQuantity);
        transportTypeSelect.addEventListener('change', updateQuantity);
    }
}

// 处理日期输入格式
function setupDateInputs() {
    // 选择所有日期输入框，包括DateField类型的输入框
    const dateInputs = document.querySelectorAll('input[data-date-format], input[type="date"], input[type="month"]');
    dateInputs.forEach(input => {
        // 设置输入框类型为text，以便自定义格式
        if (input.type !== 'text') {
            input.type = 'text';
        }
        
        // 格式化已有的日期值为yyyy-mm格式
        if(input.value) {
            const date = new Date(input.value);
            if(!isNaN(date.getTime())) {
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                input.value = `${year}-${month}`;
            }
        }
        
        // 添加placeholder提示
        if (!input.placeholder) {
            input.placeholder = 'YYYY-MM';
        }
        
        // 添加输入验证
        input.addEventListener('input', function() {
            // 允许用户输入年份和月份，格式为YYYY-MM
            let value = this.value.replace(/[^0-9-]/g, '');
            
            // 如果输入了分隔符，确保只有一个
            const parts = value.split('-');
            if (parts.length > 2) {
                value = parts[0] + '-' + parts.slice(1).join('');
            }
            
            // 限制年份为4位数
            if (parts[0] && parts[0].length > 4) {
                parts[0] = parts[0].substring(0, 4);
                value = parts.join('-');
            }
            
            // 限制月份为2位数
            if (parts[1] && parts[1].length > 2) {
                parts[1] = parts[1].substring(0, 2);
                value = parts.join('-');
            }
            
            this.value = value;
        });
        
        // 添加失去焦点时的验证
        input.addEventListener('blur', function() {
            const value = this.value;
            if (!value) return;
            
            const parts = value.split('-');
            if (parts.length !== 2) return;
            
            const year = parseInt(parts[0], 10);
            let month = parseInt(parts[1], 10);
            
            // 验证年份和月份
            if (isNaN(year) || isNaN(month) || year < 1900 || year > 2100 || month < 1 || month > 12) {
                return;
            }
            
            // 格式化为YYYY-MM
            month = String(month).padStart(2, '0');
            this.value = `${year}-${month}`;
        });
    });
}

// Initialize all form handlers
document.addEventListener('DOMContentLoaded', function() {
    updateContractName();
    setupPriceCalculation();
    setupContractDetails();
    setupTransportQuantity();
    setupDateInputs();
}); 