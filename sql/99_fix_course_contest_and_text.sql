SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

ALTER TABLE course_registrations MODIFY user_id INT NULL;
ALTER TABLE contest_registrations MODIFY user_id INT NULL;

UPDATE ddj SET description = '專業 2 頻道 DJ 控制器，適合進階 DJ' WHERE name = 'Pioneer DDJ-800';
UPDATE ddj SET description = '中階 DJ 控制器，初學者推薦' WHERE name = 'Numark Mixtrack Pro 3';
UPDATE ddj SET description = '經濟實惠的 DJ 控制器' WHERE name = 'Reloop Beatmix 2';

UPDATE audio SET description = '高品質黑膠唱盤' WHERE name = 'Pioneer PLX-500 Turntable';
UPDATE audio SET description = '專業 DJ 耳機，清晰音質' WHERE name = 'Technics EAH-DJ1200 Headphones';
UPDATE audio SET description = '專業 DJ 混音機' WHERE name = 'Numark NS7III Mixer';

UPDATE wire SET description = '專業 XLR 平衡線' WHERE name = 'Neutrik Pro XLR Cable';
UPDATE wire SET description = '高品質 USB 傳輸線' WHERE name = 'Hosa USB-210AF USB Cable';
UPDATE wire SET description = '立體聲 3.5mm 連接線' WHERE name = 'Hosa 3.5mm TRS Cable';

UPDATE music SET description = '現代電子音樂作品' WHERE title = 'Electronize';
UPDATE music SET description = '充滿能量的浩室舞曲' WHERE title = 'House Energy';
UPDATE music SET description = '技術性科技音樂' WHERE title = 'Tech Groove';

UPDATE courses SET
    title = 'DJ 初級入門課程',
    description = '適合完全初學者，從基礎開始教起',
    syllabus = '基礎概念、設備認識、混音技巧'
WHERE id = 1;

UPDATE courses SET
    title = 'DJ 中級進階課程',
    description = '適合有基礎的 DJ 學習進階技巧',
    syllabus = '進階混音、特效應用、表演技巧'
WHERE id = 2;

UPDATE courses SET
    title = 'DJ 專業精英課程',
    description = '最高級別的 DJ 課程，面向職業人士',
    syllabus = '專業表演、音樂製作、舞台控制'
WHERE id = 3;

UPDATE contests SET
    title = '中部 DJ 大賽 2026',
    description = '台中地區最大規模的 DJ 競技場',
    venue = '台中市中友百貨 12F'
WHERE id = 1;

UPDATE contests SET
    title = '全國 DJ 總決賽',
    description = '全台各地 DJ 高手匯聚一堂',
    venue = '台北市信義區'
WHERE id = 2;

UPDATE contests SET
    title = '春季 DJ 挑戰賽',
    description = '新手友善的 DJ 比賽',
    venue = '台中市西屯區'
WHERE id = 3;

SET FOREIGN_KEY_CHECKS = 1;
